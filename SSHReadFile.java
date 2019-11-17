import com.jcraft.jsch.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class SSHReadFile {
    private String user, host, password, directory, file;
    private Session JSchSession;
    private ChannelSftp sftp;
    private Channel JSchChannel;

    public SSHReadFile(String user, String host, String password, String directory) {
        this.user = user;
        this.host = host;
        this.password = password;
        this.directory = directory;
      
    }

    public SSHReadFile(String user, String host, String directory) {
        this(user, host, null, directory);
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
            JSchChannel = JSchSession.openChannel("sftp");
            JSchChannel.connect();
            sftp = (ChannelSftp) JSchChannel;
            sftp.cd(directory);

        } catch (JSchException e) {
            e.printStackTrace();
        } catch (SftpException e) {
            e.printStackTrace();
        }
    }

    public String readFile(String file) {
        StringBuilder sb = new StringBuilder();
        try {

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

        } catch (IOException e) {
            e.printStackTrace();
        } catch (SftpException e) {
            e.printStackTrace();
        }

        return sb.toString();

    }

    public void close() {
        sftp.exit();
        sftp.disconnect();
        JSchChannel.disconnect();
        JSchSession.disconnect();
    }
}
