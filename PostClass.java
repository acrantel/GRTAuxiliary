import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public class PostClass {
    public static void main(String args[]) {
        // Read every line from lidar test data and send them all to flask
        try {
            String user = "aaryan";//"admin";
            String host = "192.168.0.110";//"10.1.92.2";
            String directory = "/Users/aaryan/Documents";//"/home/lvuser/deploy/";
            String password = "";
            String file = "data.txt";

            // Can be new SSHReadFile(user, host, password);
            SSHReadFile ssh = new SSHReadFile(user, host);
            // Opens the ssh session so you don't have to connect every time
            ssh.connectSSH();
            
            int x = 600;
            int y = 300;

            // Eventually make it so only reads when file updated
            for (int i = 0; i < 100; i++) {
                String fileContent = ssh.readFile(directory, file);
                String[] contentSplit = fileContent.split("\n");
                // Want to make payload a 2D array string
                String payload = "["; 
                for (String s : contentSplit) {
                    String[] point = s.split(" ");
                    // From lidar, r is given as 00000.00 which cannot be processed, turning into double then string makes it a valid number
                    String[] numData = { point[1], Double.toString(Double.parseDouble(point[3])), point[5]};
                    payload += Arrays.toString(numData) + ",";
                }
            
                // Spaces require a special token to be passed, easier to just remove since don't need
                payload = payload.replaceAll(" ", "");
                // There will be an extra comma at the end from the while loop
                payload = payload.substring(0, payload.length() - 1);
                payload += "]";

                System.out.println(payload);
                go("getlidardata", payload);

                // Simulate getting new pos data
                x += (int) (Math.random()*50-25);
                y += (int) (Math.random()*50-25);
                System.out.println(x + " " + y);
                go("getposdata", "["+x+","+y+"]");

                // Simulate data getting updated
                Thread.sleep(200);
            }

            // Resource leaks aren't good
            ssh.closeSSH();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void go(String page, String inputData) {
        HttpURLConnection conn = null;
        DataOutputStream os = null;
        // Connect to the flask page requested with whatever input
        try {
            URL url = new URL("http://127.0.0.1:5000/" + page + "/"); // important to add the trailing slash
            byte[] postData = inputData.getBytes(StandardCharsets.UTF_8);
            conn = (HttpURLConnection) url.openConnection();
            conn.setDoOutput(true);
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setRequestProperty("charset", "utf-8");
            conn.setRequestProperty("Content-Length", Integer.toString(inputData.length()));
            os = new DataOutputStream(conn.getOutputStream());
            os.write(postData);
            os.flush();

            if (conn.getResponseCode() != 200) {
                throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
            }

            conn.disconnect();

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (conn != null) {
                conn.disconnect();
            }
        }
    }
}