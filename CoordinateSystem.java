/**
 * A class designed to represent a 2D coordinate system
 * 
 * Intended to be used with 2/3 Axis Table using integer based encoder values
 */
public class CoordinateSystem {
    private int[][][] coordinates; // Stores the coordinate for each square

    // Maxima
    private int maxX; 
    private int maxY;

    // How big of a "jump" between each square?
    private double xJump;
    private double yJump;

    // Number of rows & columns (rows on x and col on y)
    private int rows;
    private int columns;

    /**
     * Creates a new CoordinateSystem object
     * 
     * @param rows Number of rows
     * @param columns Number of columns 
     * @param mX Maximum x value (corner)
     * @param mY Maximum y value (corner)
     */
    public CoordinateSystem(int rows, int columns, int mX, int mY) {
        /**
         * Technically a 3D array however the most inner array represents the 
         * x and y coordinates of the square
         */
        coordinates = new int[rows][columns][2]; // New "3D" array (see above)

        // Assigning variables
        this.rows = rows;
        this.columns = columns;
        maxX = mX;
        maxY = mY;

        fillCoords(); // Fills the the coordinate system with the proper coordinates
    }

    /**
     * Fills in the coordinates array using the size (maxima and rows/columns)
     */
    public void fillCoords() {
        // Stored as doubles for more precision later
        xJump = (double) maxX / (rows - 1);
        yJump = (double) maxY / (columns - 1);

        // Loops through every square
        for (int row = 0; row < coordinates.length; row++) {
            for (int col = 0; col < coordinates[0].length; col++) {
                // Multiplies the jump by the row/col of the square
                int x = (int) Math.round(xJump * row); // Cast to int because Math.round(double)
                int y = (int) Math.round(yJump * col); // returns a long
                coordinates[row][col] = new int[] { x, y }; // Saving coordinates to array
            }
        }
    }

    // ACCESSOR METHODS

    /**
     * Finds the x-y coordinates of a square
     * @param row The row of the array (zero indexed)
     * @param col The column of the array (zero indexed)
     * @return Array containing x-y coordinates where array[0] is the x coordinate
     */
    public int[] getCoords(int row, int col) {
        return coordinates[row][col];
    }

    /**
     * Finds the middle coordinate between 2 squares
     * 
     * Intended to find the edge/corner between adjacent squares but 
     * can be used in other ways
     * @param row1 Row of first square
     * @param col1 Column of first square
     * @param row2 Row of second square 
     * @param col2 Column of second square
     * @return An int array containing a pair of x-y coordinates 
     */
    public int[] getHalfCoords(int row1, int col1, int row2, int col2) {
        int[] coords1 = getCoords(row1, col1);
        int[] coords2 = getCoords(row2, col2);

        int[] coordsF;

        int x1 = coords1[0];
        int y1 = coords1[1];

        int x2 = coords2[0];
        int y2 = coords2[1];

        coordsF = new int[] { (Math.round((float) (x1 + x2) / 2)), (Math.round((float) (y1 + y2) / 2)) };

        return coordsF;
    }

    /**
     * Gets number of rows in the board
     * @return Int number of rows
     */
    public int getRows() {
        return rows;
    }

    /**
     * Gets number of columns in the board
     * @return Int number of columns
     */
    public int getCols() {
        return columns;
    }

    /**
     * Gets the X distance between the center of each square
     * @return Int distance
     */
    public double getXJump() {
        return xJump;
    }

    /**
     * Gets the Y distance between the center of each square
     * @return Int distance 
     */
    public double getYJump() {
        return yJump;
    }

    // MODIFIER METHODS

    /**
     * Changes the number of rows & columns
     * 
     * WARNING: Clears the array
     * @param rows New number of rows
     * @param columns New number of columns
     */
    public void reshape(int rows, int columns) {
        coordinates = new int[rows][columns][2]; // New array

        // Changes rows and columns
        this.rows = rows;
        this.columns = columns;

        fillCoords(); // Refills coordinate array
    }

    /**
     * Sets new maximum X value
     * @param mX New maxX
     */
    public void setMaxX(int mX) {
        maxX = mX;
    }

    /**
     * Sets new maximum Y value
     * @param mY New maxY
     */
    public void setMaxY(int mY) {
        maxY = mY;
    }

    
    /**
     * A String representation of the coordinate array, formatted for ease of reading
     * @param maxLen The maximum length of the coordinates (minus extra formatting)
     * @return String
     */
    public String toString(int maxLen) {
        maxLen += 3; // For 3 extra characters added
        String str = ""; // Start of string

        /**
         * Loops through each square and adds extra formatting to make the data more readable.
         * 
         * Then adds whitespace after to reach maxLen
         * 
         * Adds new line after each row
         */
        for (int[][] row : coordinates) {
            for (int[] col : row) {
                String temp = "|" + (int) col[0] + ", " + col[1];
                int len = temp.length();
                for (int i = maxLen; i > len; i--) {
                    temp += " ";
                }
                str += temp;
            }
            str += "\n";
        }
        return str;
    }

    /**
     * A String representation of the coordinate array, formatted for ease of reading.
     * 
     * Use toString(int maxLen) for larger coordinates (above 1000)
     * @return String
     */
    public String toString() {
        return toString(13);
    }
}


/**
 * Tester class
 */
class CoordTest {
    public static void main(String[] args) {
        CoordinateSystem board = new CoordinateSystem(8, 8, -3175, -628);

        System.out.println(board);

        System.out.println(board.getHalfCoords(0, 0, 1, 0)[0] + " " + board.getHalfCoords(0, 0, 1, 0)[1]);
    }
}