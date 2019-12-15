import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public class PostClass {
    public static SSHReadFile ssh;

    public static void main(String args[]) {

        // Read every line from lidar test data and send them all to flask

        String user =  "aaryan";
                //"pi";
        String host =  "192.168.0.106";
                //"10.1.92.50";
        String directory =  "/Users/aaryan/Documents";
                //"/home/pi/Documents/GRTLidar";
        String password = "";

        SSHReadFile ssh = new SSHReadFile(user, host, password, directory);
        // Opens the ssh session so you don't have to connect every time
        ssh.connectSSH();

        // position in mm
        String x = "8230";
        String y = "4000";
        String fileContentData;
        String fileContentPos;

        long currTime = System.currentTimeMillis();
        System.out.println("Starting");

        // stop automatically after 5 minutes
        while (System.currentTimeMillis() - currTime < 300000) {

            // lidar data is written to this
            fileContentData = ssh.readFile("data.txt");
           // System.out.println(fileContentData);
            String[] contentSplit = fileContentData.split("\n");
            //System.out.println();
            // for (int k = 0; k < contentSplit.length; k++) {
            //     System.out.println(contentSplit[k]);
            // }
            // Want to make payload a 2D array string
            String payload = "[";
            for (String s : contentSplit) {
                String[] point = s.split(" ");

                // From lidar, r is given as 00000.00 which cannot be processed, turning into
                // double then string makes it a valid number
                // for (int i = 0; i < point.length; i++) {
                //     System.out.println(point.length + " " + point[i]);
                // }
                String[] numData = { point[1], Double.toString(Double.parseDouble(point[3])), point[5] };
                payload += Arrays.toString(numData) + ",";
            
            }

            // Spaces require a special token to be passed, easier to just remove since
            // don't need
            payload = payload.replaceAll(" ", "");

            // There will be an extra comma at the end from the while loop
            payload = payload.substring(0, payload.length() - 1);

            payload += "]";

            
            go("getlidardata", payload);

            fileContentPos = ssh.readFile("pos.txt");
           // System.out.println(fileContentPos);
            String[] pos = fileContentPos.split(" ");
            x = pos[0];
            y = pos[1];

            go("getposdata", "[" + x + "," + y + "]");
        }

        // Resource leaks aren't good
        ssh.close();
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