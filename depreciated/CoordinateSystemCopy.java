package depreciated;

@Deprecated
public class CoordinateSystemCopy {
    
    /* Declare OpMode members. */
    private Square[][] board;
    private int maxX;
    private int squareSizeX;
    private int squareSizeY;

    public CoordinateSystemCopy(Square[][] b, int sqLenX, int sqLenY, int maxX) {
        board = b.clone();
        this.maxX = maxX;
        //squareSizeX = Math.round((sqLenX + ((float)maxX/board.length))/2);
        squareSizeX = sqLenX;
        squareSizeY = sqLenY;

    }

    public CoordinateSystemCopy(int sqLenX, int sqLenY, int maxX) {
        board = new Square[8][8]; // Standard chess board size
        this.maxX = maxX;
        //squareSizeX = Math.round((sqLenX + ((float)maxX/board.length))/2);
        squareSizeX = sqLenX;
        squareSizeY = sqLenY;
    }

    public void setSquare(String name, int row, int col) {
        int[] coords = getCoords(row, col);
        Square s = new Square(name, coords[0], coords[1]);
        board[row][col] = s;
    }

    public int[] getCoords(int row, int col) {
        row++;
        col++;

        double x1 = squareSizeX * row;
        double x2 = (double)maxX/board.length;
        int x = Math.round(((float)(x1+x2)/2) - ((float)squareSizeX/2));
        int y = Math.round((squareSizeY * col) - ((float)squareSizeY/2));

        return new int[] { x, y };
    }

    public int[] findCorner(String c, int row, int col) {
        int[] coords = getCoords(row, col);
        int x = coords[0];
        int y = coords[1];
        int h = Math.round((float)squareSizeX/2);
        int xH = Math.round((float)squareSizeY/2);
        switch (c) {
            case "BL":
                return new int[] { x - xH, y - h };
            case "BR":
                return new int[] { x + xH, y - h };
            case "TL":
                return new int[] { x - xH, y + h };
            case "TR":
                return new int[] { x + xH, y + h };
            default:
                return new int[1];
        }
    }

    public Square getSquare(int row, int col) {
        return board[row][col];
    }

    public int getSquareSizeX() {
        return squareSizeX;
    }

    public int getSquareSIzeY() {
        return squareSizeY;
    }

    //private double xToY(int x) {
    //    return x * (squareSizeX / squareSizeY);
    //}

    //private double yToX(int y) {
    //    return y * (squareSizeY / squareSizeX);
    //}
}
