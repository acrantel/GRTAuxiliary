import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class PostClass {
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

    public static String goGet(String page) {
        HttpURLConnection conn = null;
        StringBuilder sb = new StringBuilder();
        // Connect to the flask page requested
        try {
            URL url = new URL("http://127.0.0.1:5000/" + page + "/"); // important to add the trailing slash
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));

            if (conn.getResponseCode() != 200) {
                throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
            }

            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line + "\n");
            }

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (conn != null) {
                conn.disconnect();
            }
        }

        return sb.toString();
    }
}