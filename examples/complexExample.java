public class ComplexExample {

    private int count;
    private String name;

    public ComplexExample(String name) {
        this.name = name;
        this.count = 0;
    }

    public void incrementCount(int value) {
        this.count += value;
    }

    public int getCount() {
        return this.count;
    }

    public boolean isEven(int number) {
        return number % 2 == 0;
    }

    public static void main(String[] args) {
        ComplexExample example = new ComplexExample("Teste");

        for (int i = 0; i < 10; i++) {
            example.incrementCount(1);
        }

        if (example.isEven(example.getCount())) {
            System.out.println(example.name + " has an even count: " + example.getCount());
        } else {
            System.out.println(example.name + " has an odd count: " + example.getCount());
        }
    }
}
