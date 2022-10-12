module SSDD {
    exception ZeroDivisionError{};

    interface Calculator {
        float sum(float a, float b);
        float sub(float a, float b);
        float mult(float a, float b);
        float div(float a, float b) throws ZeroDivisionError;
    };

    interface CalculatorTester {
        void test(Calculator* calculator);
    };
};
