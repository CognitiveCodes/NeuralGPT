import org.apache.commons.io.FilenameUtils;
import org.commonmark.node.Node;
import org.commonmark.parser.Parser;
import org.commonmark.renderer.html.HtmlRenderer;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class TextToMarkdownConverter {

    public static void main(String[] args) throws IOException {
        String textFilePath = "C:/path/to/text/file.txt";
        String destinationFolder = "E:/AI/NeuralGPT/NeuralGPT";

        File file = new File(textFilePath);
        String fileExtension = FilenameUtils.getExtension(file.getName());

        String markdownFileName = FilenameUtils.removeExtension(file.getName()) + ".md";
        Path markdownFilePath = Paths.get(destinationFolder, markdownFileName);

        String text = Files.readString(file.toPath());
        String markdown = convertToMarkdown(text, fileExtension);

        Files.writeString(markdownFilePath, markdown);
    }

    private static String convertToMarkdown(String text, String fileExtension) {
        Parser parser = null;
        if (fileExtension.equals("txt")) {
            parser = Parser.builder().build();
        } else if (fileExtension.equals("docx")) {
            parser = new DocxToMarkdownParser();
        } else if (fileExtension.equals("pdf")) {
            parser = new PdfToMarkdownParser();
        }

        Node document = parser.parse(text);
        HtmlRenderer renderer = HtmlRenderer.builder().build();
        return renderer.render(document);
    }
}