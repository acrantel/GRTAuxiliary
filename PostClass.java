import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Scanner;

public class PostClass {
    public static void main(String args[]) {
        // Read every line from lidar test data and send them all to flask
        try {
            File inputFile = new File("data.txt");
            Scanner sc = new Scanner(inputFile);
            String payload = "[";
            while (sc.hasNextLine()) {
                String[] split = sc.nextLine().split(" ");
                // From lidar, r is given as 00000.00 which cannot be processed, turning into double then string makes it a valid number
                String[] numData = { split[1], Double.toString(Double.parseDouble(split[3])), split[5]};
                payload += Arrays.toString(numData) + ",";
            }
            // Spaces require a special token to be passed, easier to just remove since don't need
            payload = payload.replaceAll(" ", "");

            // There will be an extra comma at the end from the while loop
            payload = payload.substring(0, payload.length() - 1);
            payload += "]";
            System.out.println(payload);
            go("getlidardata", payload);

            // Simulate getting new data every 200ms 100 times
            int x = 600;
            int y = 300;
            for (int i = 0; i < 100; i++) {
                x += (int) (Math.random()*50-25);
                y += (int) (Math.random()*50-25);
                System.out.println(x + " " + y);
                go("getposdata", "["+x+","+y+"]");
                Thread.sleep(200);
            }
            sc.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void go(String page, String inputData) {
        HttpURLConnection conn = null;
        DataOutputStream os = null;
        // Connect to the flask page requested with whatever input
        try {
            URL url = new URL("http://127.0.0.1:5000/" + page + "/"); // important to add the trailing slash after add
            // System.out.println(input);
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

            // How you would read from flask
            // BufferedReader br = new BufferedReader(new InputStreamReader(
            // (conn.getInputStream())));

            // String output;
            // System.out.println("Output from Server ....");
            // while ((output = br.readLine()) != null) {
            // System.out.println(output);
            // }

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