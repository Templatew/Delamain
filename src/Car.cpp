/**
 * @file Car.cpp
 * @brief Implementation of the Car class.
 */

#include "Car.hpp"

Car::Car(double startX, double startY)
    : m_x(startX)
    , m_y(startY)
    , m_width(60.0)   // Car width in pixels
    , m_height(30.0)  // Car height in pixels
    , m_speed(5.0)    // Movement speed in pixels per frame
{
}

void Car::moveUp()
{
    m_y -= m_speed;
}

void Car::moveDown()
{
    m_y += m_speed;
}

void Car::moveLeft()
{
    m_x -= m_speed;
}

void Car::moveRight()
{
    m_x += m_speed;
}

void Car::update()
{
    // Future: Add physics, momentum, or other per-frame logic here
    // Currently, movement is handled directly by move methods
}

QRectF Car::getBoundingRect() const
{
    return QRectF(m_x, m_y, m_width, m_height);
}
