import com.jcraft.jsch.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class SSHReadFile {
    private String user, host, password;
    private Session JSchSession;

    public SSHReadFile(String user, String host, String password) {
        this.user = user;
        this.host = host;
        this.password = password;
    }

    public SSHReadFile(String user, String host) {
        this.user = user;
        this.host = host;
    }

    public void connectSSH() {
        try {
            JSch jsch = new JSch();
            JSchSession = jsch.getSession(user, host);
            JSchSession.setPort(22);
            if (password != null)
                JSchSession.setPassword(password);
            JSchSession.setConfig("StrictHostKeyChecking", "no");
            JSchSession.connect();

        } catch (JSchException e) {
            System.out.println(e.getStackTrace());
        }
    }

    public void closeSSH() {
        JSchSession.disconnect();
    }

    public String readFile(String directory, String file) {
        StringBuilder sb = new StringBuilder();
        try {
            Channel JSchChannel = JSchSession.openChannel("sftp");
            JSchChannel.connect();
            ChannelSftp sftp = (ChannelSftp) JSchChannel;
            sftp.cd(directory);
            InputStream input = sftp.get(file);
            Reader read = new InputStreamReader(input, StandardCharsets.UTF_8);
            BufferedReader br = new BufferedReader(read);
            String line;

            while ((line = br.readLine()) != null) {
                sb.append(line + "\n");
            }

            br.close();
            read.close();
            input.close();
            sftp.disconnect();
            JSchChannel.disconnect();

        } catch (JSchException e) {
            e.printStackTrace();
        } catch (SftpException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return sb.toString();
    }
}
