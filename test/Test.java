import java.util.Arrays;
import java.util.List;

public class Test {
    public static void main(String[] args) {
        // Prints "Hello, World" to the terminal window.
        String str = "$科技$$tech$$商业$";
        // List<String> items = Arrays.asList(str.split("$$"));
        for (String item:str.split("\\$\\$"))
            System.out.println(item);
    }


}