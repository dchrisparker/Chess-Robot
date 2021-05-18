package depreciated;

@Deprecated
public class Square {
    public String piece;
    public int x;
    public int y;

    public Square(String n, int xCoord, int yCoord) {
        piece = n;
        x = xCoord;
        y = yCoord;
    }

    public void setX(int nX) {
        x = nX;
    }
    
    public void setY(int nY) {
        y = nY;
    }

    public Square copy() {
        return new Square(piece, x, y);
    }

    public boolean equals(Square s) {
        return piece.equals(s.piece);
    }
}
