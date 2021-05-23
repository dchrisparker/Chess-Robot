package engine;

import java.io.*;
import java.util.stream.Collectors;

public class UCIEngine {
    private final String PATH;
    private final File DIR;
    private Process p;
    private Runtime rt;
    
    /**
     * Initializes the chess engine 
     * @param path Path of the engine executable (including .exe)
     * @throws IOException If path does not exist or cannot be accessed
     */
    public UCIEngine(String path) throws IOException {
        PATH = path;
        rt = Runtime.getRuntime();
        p = rt.exec(PATH);
        DIR = new File(PATH);
        BufferedReader output = new BufferedReader(new InputStreamReader(p.getInputStream()));
        
        System.out.println(output.lines().collect(Collectors.joining(System.lineSeparator())));
    }

    // public String exec(String command) throws IOException{
    //      rt.exec(command, null, DIR);
    // }
    
    // ACCESSOR METHODS
    public String getPath() {
        return PATH;
    }
}

class UCITest {
    public static void main(String[] args) throws IOException {
        UCIEngine engine = new UCIEngine("C:/Users/chris/Desktop/stockfish_13_win_x64_bmi2/stockfish_13");
    }
}
