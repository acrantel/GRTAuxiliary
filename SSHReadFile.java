import com.jcraft.jsch.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class SSHReadFile {
    private String user, host, password, directory, file;
    
    public SSHReadFile (String user, String host, String password, String directory, String file) {
        this.user = user;
        this.host = host;
        this.password = password;
        this.directory = directory;
        this.file = file;
    }

    public SSHReadFile (String user, String host, String directory, String file) {
        this.user = user;
        this.host = host;
        this.directory = directory;
        this.file = file;
    }

    public String readFile() {
        JSch jsch = new JSch();
        StringBuilder stringBuild = new StringBuilder();
        try {
            Session JSchSession = jsch.getSession(user, host);
            JSchSession.setPort(22);

            if (password != null) JSchSession.setPassword(password);

            JSchSession.setConfig("StrictHostKeyChecking", "no");
            JSchSession.connect();
            Channel JSchChannel = JSchSession.openChannel("sftp");
            JSchChannel.connect();
            ChannelSftp sftp = (ChannelSftp) JSchChannel;
            sftp.cd(directory);
            InputStream input = sftp.get(file);

            // http://programmerclubhouse.com/index.php/reading-and-writing-linux-files-using-jsch-java/
            // TODO: Figure out why buffer is needed
            
            char[] buffer = new char[0x10000];
            Reader read = new InputStreamReader(input, StandardCharsets.UTF_8);
            int int_Line;
            do {
                int_Line = read.read(buffer, 0, buffer.length);
                if (int_Line > 0) {
                    stringBuild.append(buffer, 0, int_Line);
                }
            }
            while (int_Line >= 0);
            read.close();
            input.close();
            sftp.exit();
            JSchChannel.disconnect();
            JSchSession.disconnect();
        }
        catch (Exception ex)
        {
            ex.printStackTrace();
        }
        return stringBuild.toString();
    }
}
