import java.util.Arrays;

public class LidarTest {
    public static void main(String args[]) {
        // Read every line from lidar test data and send them all to flask
        String user = "aaryan";
        // "pi";
        String host = "192.168.0.105";
        // "10.1.92.50";
        String directory = "/Users/aaryan/Documents";
        // "/home/pi/Documents/GRTLidar";
        String password = "";

        SSHReadFile ssh = new SSHReadFile(user, host, password, directory);
        // Opens the ssh session so you don't have to connect every time
        ssh.connectSSH();

        // position in mm
        String x = "6000";
        String y = "3000";
        String fileContentData;
        String fileContentPos;

        System.out.println("Starting");

        // stop automatically after some time (10sec)
        long currTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - currTime < 10000) {

            // lidar data is written to this
            fileContentData = ssh.readFile("data.txt");
            String[] contentSplit = fileContentData.split("\n");

            // Want to make payload a 2D array string
            String payload = "[";
            for (String s : contentSplit) {
                String[] point = s.split(" ");

                // From lidar, r is given as 00000.00 which cannot be processed, turning into
                // double then string makes it a valid number

                // might be 4,6,8 if the leading bits are included
                String[] numData = { point[1], Double.toString(Double.parseDouble(point[3])), point[5] };
                payload += Arrays.toString(numData) + ",";

            }

            // Spaces require a special token to be passed, easier to just remove since don't need
            payload = payload.replaceAll(" ", "");

            // There will be an extra comma at the end from the while loop
            payload = payload.substring(0, payload.length() - 1);
            payload += "]";

            PostClass.goPost("getlidar", payload);

            fileContentPos = ssh.readFile("pos.txt");

            String[] pos = fileContentPos.split(" ");
            x = pos[0];
            y = pos[1];

            PostClass.goPost("getpos", "[" + x + "," + y + "]");
        }
        // Resource leaks aren't good
        ssh.close();
    }
}