import java.util.HashMap;
import com.google.gson.*;

public class OtherTest {
    public static void main(String args[]) {
        String buttonClick = PostClass.goGet("buttondata");
        String canvasClick = PostClass.goGet("canvasdata");
        System.out.println("Button clicked: " + buttonClick.replace("\n", ""));
        System.out.println("Canvas spot clicked: " + canvasClick.replace("\n", ""));

        PostClass.goPost("starttimer", "true");

        HashMap<String, Integer> working = new HashMap<>();
        working.put("fl", 1);
        working.put("fr", 0);
        working.put("bl", 1);
        working.put("br", 1);
        PostClass.goPost("swervedata", new Gson().toJson(working));

        PostClass.goPost("lemondata", "5");
    }
}