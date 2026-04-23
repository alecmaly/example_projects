package mono.shared;

public interface Shape {
    double area();
    default String describe() { return getClass().getSimpleName() + " area=" + area(); }
}
