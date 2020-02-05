import java.util.HashMap;
import com.google.gson.*;
import java.util.ArrayList;

public class OtherTest {
    public static void main(String args[]) {
        String buttonClick = PostClass.goGet("buttondata");
        String canvasClick = PostClass.goGet("canvasdata");
        System.out.println("Button clicked: " + buttonClick.replace("\n", ""));
        System.out.println("Canvas spot clicked: " + canvasClick.replace("\n", ""));

        PostClass.goPost("starttimer", "true");

        HashMap<String, Integer> working = new HashMap<>();
        working.put("fl", 0);
        working.put("fr", 1);
        working.put("bl", 1);
        working.put("br", 1);
        PostClass.goPost("swervedata", new Gson().toJson(working));

        PostClass.goPost("lemondata", "4");

        ArrayList<int[]> points = new ArrayList<>();
        points.add(new int[] { 1, 1 });
        points.add(new int[] { 100, 100 });
        points.add(new int[] {200,0});
        points.add(new int[] {500,300});
        PostClass.goPost("getlidar", new Gson().toJson(points));

        for (int i = 0; i < 360; i++) {
            PostClass.goPost("angledata", Integer.toString(i));
            try {
                Thread.sleep(25);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}