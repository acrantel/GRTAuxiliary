public class OtherTest {
    public static void main(String args[]) {
        String buttonClick = PostClass.goGet("buttondata");
        String canvasClick = PostClass.goGet("canvasdata");
        System.out.println("Button clicked: " + buttonClick.replace("\n", ""));
        System.out.println("Canvas spot clicked: " + canvasClick.replace("\n", ""));

        PostClass.goPost("starttimer", "true");
    }
}