#ifndef CAR_HPP
#define CAR_HPP

#include <QRectF>

/**
 * @class Car
 * @brief Represents a simple 2D car with position and movement capabilities.
 * 
 * The car is represented as a rectangle that can move in four directions
 * based on keyboard input.
 */
class Car
{
public:
    /**
     * @brief Construct a new Car object
     * @param startX Initial X position
     * @param startY Initial Y position
     */
    Car(double startX = 100.0, double startY = 100.0);

    // Movement control methods
    void moveUp();
    void moveDown();
    void moveLeft();
    void moveRight();

    /**
     * @brief Update car state (called each frame)
     * Currently handles any per-frame logic
     */
    void update();

    // Getters
    double getX() const { return m_x; }
    double getY() const { return m_y; }
    double getWidth() const { return m_width; }
    double getHeight() const { return m_height; }
    
    /**
     * @brief Get the bounding rectangle of the car
     * @return QRectF representing the car's bounds
     */
    QRectF getBoundingRect() const;

    // Setters
    void setSpeed(double speed) { m_speed = speed; }
    void setPosition(double x, double y) { m_x = x; m_y = y; }

private:
    double m_x;        ///< X position (left edge)
    double m_y;        ///< Y position (top edge)
    double m_width;    ///< Car width in pixels
    double m_height;   ///< Car height in pixels
    double m_speed;    ///< Movement speed in pixels per update
};

#endif // CAR_HPP
