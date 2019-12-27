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
        String host =  "192.168.0.108";
                //"10.1.92.50";
        String directory =  "/Users/aaryan/Documents";
                //"/home/pi/Documents/GRTLidar";
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

        // stop automatically after some time
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

            goPost("getlidardata", payload);

            fileContentPos = ssh.readFile("pos.txt");
           
            String[] pos = fileContentPos.split(" ");
            x = pos[0];
            y = pos[1];

            goPost("getposdata", "[" + x + "," + y + "]");
            goGet("givebuttondata");
            goGet("givecanvasclick");
        }
        // Resource leaks aren't good
        ssh.close();
    }

    public static void goPost(String page, String inputData) {
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

            BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
            String line;
            
            while ((line = br.readLine()) != null) {
                System.out.println(line);
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

    public static void goGet(String page) {
        HttpURLConnection conn = null;
        // Connect to the flask page requested with whatever input
        try {
            URL url = new URL("http://127.0.0.1:5000/" + page + "/"); // important to add the trailing slash
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
            String line;
            
            while ((line = br.readLine()) != null) {
                System.out.println(line);
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