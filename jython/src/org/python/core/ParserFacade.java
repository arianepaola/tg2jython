// Copyright (c) Corporation for National Research Initiatives
package org.python.core;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.UnsupportedCharsetException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.antlr.runtime.CharStream;
import org.antlr.runtime.CommonTokenStream;

import org.python.antlr.BaseParser;
import org.python.antlr.ExpressionParser;
import org.python.antlr.InteractiveParser;
import org.python.antlr.ParseException;
import org.python.antlr.ModuleParser;
import org.python.antlr.NoCloseReaderStream;
import org.python.antlr.PythonTree;
import org.python.antlr.PythonLexer;
import org.python.antlr.PythonPartial;
import org.python.antlr.PythonTokenSource;
import org.python.antlr.base.mod;
import org.python.core.io.StreamIO;
import org.python.core.io.TextIOInputStream;
import org.python.core.io.UniversalIOWrapper;
import org.python.core.util.StringUtil;

/**
 * Facade for the classes in the org.python.antlr package.
 */
public class ParserFacade {

    private static int MARK_LIMIT = 100000;

    private ParserFacade() {}

    private static String getLine(BufferedReader reader, int line) {
        if (reader == null) {
            return "";
        }
        String text = null;
        try {
            for (int i = 0; i < line; i++) {
                text = reader.readLine();
            }
            return text == null ? text : text + "\n";
        } catch (IOException ioe) {
        }
        return text;
    }

    // if reader != null, reset it
    public static PyException fixParseError(ExpectedEncodingBufferedReader reader,
                                            Throwable t,
                                            String filename) {
        if (reader != null) {
            try {
                reader.reset();
            } catch (IOException e) {
                reader = null;
            }
        }

        if (t instanceof ParseException) {
            ParseException e = (ParseException)t;
            PythonTree node = (PythonTree)e.node;
            int line=e.line;
            int col=e.charPositionInLine;
            if (node != null) {
                line = node.getLine();
                col = node.getCharPositionInLine();
            }
            String text=getLine(reader, line);
            String msg = e.getMessage();
            if (e.getType() == Py.IndentationError) {
                return new PyIndentationError(msg, line, col, text, filename);
            }
            return new PySyntaxError(msg, line, col, text, filename);
        } else if (t instanceof CharacterCodingException) {
            String msg;
            if (reader.encoding == null) {
                msg = "Non-ASCII character in file '" + filename + "', but no encoding declared"
                        + "; see http://www.python.org/peps/pep-0263.html for details";
            } else {
                msg = "Illegal character in file '" + filename + "' for encoding '"
                        + reader.encoding + "'";
            }
            throw Py.SyntaxError(msg);
        }
        else return Py.JavaError(t);
    }

    /**
     * Internal parser entry point.
     *
     * Users of this method should call fixParseError on any Throwable thrown
     * from it, to translate ParserExceptions into PySyntaxErrors or
     * PyIndentationErrors.
     */
    private static mod parse(ExpectedEncodingBufferedReader reader,
                                String kind,
                                String filename,
                                CompilerFlags cflags) throws Throwable {
        reader.mark(MARK_LIMIT); // We need the ability to move back on the
                                 // reader, for the benefit of fixParseError and
                                 // validPartialSentence
        if (kind.equals("eval")) {
            CharStream cs = new NoCloseReaderStream(reader);
            ExpressionParser e = new ExpressionParser(cs, filename, cflags.encoding);
            return e.parse();
        } else if (kind.equals("single")) {
            InteractiveParser i = new InteractiveParser(reader, filename, cflags.encoding);
            return i.parse();
        } else if (kind.equals("exec")) {
            CharStream cs = new NoCloseReaderStream(reader);
            ModuleParser g = new ModuleParser(cs, filename, cflags.encoding);
            return g.file_input();
        } else {
            throw Py.ValueError("parse kind must be eval, exec, or single");
        }
    }

    public static mod parse(InputStream stream,
                                String kind,
                                String filename,
                                CompilerFlags cflags) {
        ExpectedEncodingBufferedReader bufReader = null;
        try {
            // prepBufReader takes care of encoding detection and universal
            // newlines:
            bufReader = prepBufReader(stream, cflags, filename, false);
            return parse(bufReader, kind, filename, cflags );
        } catch (Throwable t) {
            throw fixParseError(bufReader, t, filename);
        } finally {
            close(bufReader);
        }
    }

    public static mod parse(String string,
                                String kind,
                                String filename,
                                CompilerFlags cflags) {
        ExpectedEncodingBufferedReader bufReader = null;
        try {
            bufReader = prepBufReader(string, cflags, filename);
            return parse(bufReader, kind, filename, cflags);
        } catch (Throwable t) {
            throw fixParseError(bufReader, t, filename);
        } finally {
            close(bufReader);
        }
    }

    public static mod partialParse(String string,
                                       String kind,
                                       String filename,
                                       CompilerFlags cflags,
                                       boolean stdprompt) {
        // XXX: What's the idea of the stdprompt argument?
        ExpectedEncodingBufferedReader reader = null;
        try {
            reader = prepBufReader(string, cflags, filename);
            return parse(reader, kind, filename, cflags);
        } catch (Throwable t) {
            PyException p = fixParseError(reader, t, filename);
            if (reader != null && validPartialSentence(reader, kind, filename)) {
                return null;
            }
            throw p;
        } finally {
            close(reader);
        }
    }

    private static boolean validPartialSentence(BufferedReader bufreader, String kind, String filename) {
        PythonLexer lexer = null;
        try {
            bufreader.reset();
            CharStream cs = new NoCloseReaderStream(bufreader);
            lexer = new BaseParser.PyLexer(cs);
            lexer.partial = true;
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            PythonTokenSource indentedSource = new PythonTokenSource(tokens, filename);
            tokens = new CommonTokenStream(indentedSource);
            PythonPartial parser = new PythonPartial(tokens);
            if (kind.equals("single")) {
                parser.single_input();
            } else if (kind.equals("eval")) {
                parser.eval_input();
            } else {
                return false;
            }

        } catch (Exception e) {
            return lexer.eofWhileNested;
        }
        return true;
    }

    private static class ExpectedEncodingBufferedReader extends BufferedReader {

        /**
         * The encoding from the source file, or null if none was specified and ascii is being used.
         */
        public final String encoding;

        public ExpectedEncodingBufferedReader(Reader in, String encoding) {
            super(in);
            this.encoding = encoding;
        }
    }

    private static ExpectedEncodingBufferedReader prepBufReader(InputStream input,
                                                                CompilerFlags cflags,
                                                                String filename,
                                                                boolean fromString)
            throws IOException {
        input = new BufferedInputStream(input);
        boolean bom = adjustForBOM(input);
        String encoding = readEncoding(input);

        if (encoding == null) {
            if (bom) {
                encoding = "utf-8";
            } else if (cflags != null && cflags.encoding != null) {
                encoding = cflags.encoding;
            }
        }
        if (cflags.source_is_utf8) {
            if (encoding != null) {
                throw new ParseException("encoding declaration in Unicode string");
            }
            encoding = "utf-8";
        }
        cflags.encoding = encoding;

        // Enable universal newlines mode on the input
        StreamIO rawIO = new StreamIO(input, true);
        org.python.core.io.BufferedReader bufferedIO =
                new org.python.core.io.BufferedReader(rawIO, 0);
        UniversalIOWrapper textIO = new UniversalIOWrapper(bufferedIO);
        input = new TextIOInputStream(textIO);

        Charset cs;
        try {
            // Use ascii for the raw bytes when no encoding was specified
            if (encoding == null) {
                if (fromString) {
                    cs = Charset.forName("ISO-8859-1");
                } else {
                    cs = Charset.forName("ascii");
                }
            } else {
                cs = Charset.forName(encoding);
            }
        } catch (UnsupportedCharsetException exc) {
            throw new PySyntaxError("Unknown encoding: " + encoding, 1, 0, "", filename);
        }
        CharsetDecoder dec = cs.newDecoder();
        dec.onMalformedInput(CodingErrorAction.REPORT);
        dec.onUnmappableCharacter(CodingErrorAction.REPORT);
        return new ExpectedEncodingBufferedReader(new InputStreamReader(input, dec), encoding);
    }

    private static ExpectedEncodingBufferedReader prepBufReader(String string,
                                                                CompilerFlags cflags,
                                                                String filename) throws IOException {
        byte[] stringBytes;
        if (cflags.source_is_utf8) {
            // Passed unicode, re-encode the String to raw bytes
            // NOTE: This could be more efficient if we duplicate
            // prepBufReader/adjustForBOM/readEncoding to work on Readers, instead of
            // encoding
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            Writer w = new OutputStreamWriter(out, "utf-8");
            w.write(string);
            w.close();
            stringBytes = out.toByteArray();
        } else {
            stringBytes = StringUtil.toBytes(string);
        }
        return prepBufReader(new ByteArrayInputStream(stringBytes), cflags, filename, true);
    }

    /**
     * Check for a BOM mark at the beginning of stream.  If there is a BOM
     * mark, advance the stream passed it.  If not, reset() to start at the
     * beginning of the stream again.
     *
     * Only checks for EF BB BF right now, since that is all that CPython 2.5
     * Checks.
     *
     * @return true if a BOM was found and skipped.
     * @throws ParseException if only part of a BOM is matched.
     *
     */
    private static boolean adjustForBOM(InputStream stream) throws IOException {
        stream.mark(3);
        int ch = stream.read();
        if (ch == 0xEF) {
            if (stream.read() != 0xBB) {
                throw new ParseException("Incomplete BOM at beginning of file");
            }
            if (stream.read() != 0xBF) {
                throw new ParseException("Incomplete BOM at beginning of file");
            }
            return true;
        }
        stream.reset();
        return false;
    }

    private static String readEncoding(InputStream stream) throws IOException {
        stream.mark(MARK_LIMIT);
        String encoding = null;
        BufferedReader br = new BufferedReader(new InputStreamReader(stream), 512);
        encoding = findEncoding(br);
        // XXX: reset() can still raise an IOException if a line exceeds our large mark
        // limit
        stream.reset();
        return encodingMap(encoding);
    }

    /**
     * Reads the first two lines of the reader, searching for an encoding
     * declaration.
     *
     * Note that reseting the reader (if needed) is responsibility of the caller.
     *
     * @return The declared encoding, or null if no encoding declaration is
     *         found
     */
    private static String findEncoding(BufferedReader br)
            throws IOException {
        String encoding = null;
        for (int i = 0; i < 2; i++) {
            String strLine = br.readLine();
            if (strLine == null) {
                break;
            }
            String result = matchEncoding(strLine);
            if (result != null) {
                encoding = result;
                break;
            }
        }
        return encoding;
    }

    private static String encodingMap(String encoding) {
        if (encoding == null) {
            return null;
        }
        if (encoding.equals("Latin-1") || encoding.equals("latin-1")) {
            return "ISO8859_1";
        }
        return encoding;
    }

    private static String matchEncoding(String inputStr) {
        String patternStr = "coding[:=]\\s*([-\\w.]+)";
        Pattern pattern = Pattern.compile(patternStr);
        Matcher matcher = pattern.matcher(inputStr);
        boolean matchFound = matcher.find();

        if (matchFound && matcher.groupCount() == 1) {
            String groupStr = matcher.group(1);
            return groupStr;
        }
        return null;
    }

    private static void close(BufferedReader reader) {
        try {
            if (reader != null) {
                reader.close();
            }
        } catch (IOException i) {
            // XXX: Log the error?
        }
    }

}
