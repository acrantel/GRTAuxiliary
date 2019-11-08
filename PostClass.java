import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Scanner;

public class PostClass {
    public static void main(String args[]) throws InterruptedException {
        try {
            File inputFile = new File("data.txt");
            Scanner sc = new Scanner(inputFile);
            String payload = "[";
            while (sc.hasNextLine()) {
                String[] split = sc.nextLine().split(" ");
                String[] numData = { split[1], Double.toString(Double.parseDouble(split[3])), split[5] };
                payload += Arrays.toString(numData) + ",";
            }
            payload = payload.replaceAll(" ", "");
            payload = payload.substring(0, payload.length() - 1);
            payload += "]";
            System.out.println(payload);
            go("getlidardata", payload);

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
        }
    }

    public static void go(String page, String inputData) {
        HttpURLConnection conn = null;
        DataOutputStream os = null;
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