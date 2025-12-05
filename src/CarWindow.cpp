/**
 * @file CarWindow.cpp
 * @brief Implementation of the CarWindow class.
 */

#include "CarWindow.hpp"
#include <QPainter>
#include <QKeyEvent>
#include <QPainterPath>

CarWindow::CarWindow(QWidget *parent)
    : QWidget(parent)
    , m_car(WINDOW_WIDTH / 2.0 - 30, WINDOW_HEIGHT / 2.0 - 15)  // Center the car
{
    // Set fixed window size
    setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT);

    // Enable keyboard focus
    setFocusPolicy(Qt::StrongFocus);

    // Setup timer for game loop (~60 FPS)
    connect(&m_timer, &QTimer::timeout, this, &CarWindow::updateState);
    m_timer.start(1000 / TARGET_FPS);  // ~16ms interval for 60 FPS
}

void CarWindow::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Draw background (road-like gray)
    painter.fillRect(rect(), QColor(50, 50, 50));

    // Draw some road markings (optional decoration)
    painter.setPen(QPen(Qt::white, 2, Qt::DashLine));
    painter.drawLine(0, WINDOW_HEIGHT / 2, WINDOW_WIDTH, WINDOW_HEIGHT / 2);

    // Get car bounds
    QRectF carRect = m_car.getBoundingRect();

    // Draw car body (main rectangle)
    painter.setBrush(QColor(200, 50, 50));  // Red car
    painter.setPen(QPen(Qt::black, 2));
    painter.drawRect(carRect);

    // Draw car windshield (small rectangle on top)
    double windshieldWidth = m_car.getWidth() * 0.4;
    double windshieldHeight = m_car.getHeight() * 0.6;
    double windshieldX = m_car.getX() + m_car.getWidth() * 0.5;
    double windshieldY = m_car.getY() + (m_car.getHeight() - windshieldHeight) / 2;
    
    painter.setBrush(QColor(150, 200, 255));  // Light blue windshield
    painter.drawRect(QRectF(windshieldX, windshieldY, windshieldWidth, windshieldHeight));

    // Draw wheels (4 small rectangles)
    painter.setBrush(Qt::black);
    double wheelWidth = 8;
    double wheelHeight = 10;
    
    // Front-left wheel
    painter.drawRect(QRectF(m_car.getX() + 5, m_car.getY() - 3, wheelWidth, wheelHeight));
    // Front-right wheel
    painter.drawRect(QRectF(m_car.getX() + 5, m_car.getY() + m_car.getHeight() - wheelHeight + 3, wheelWidth, wheelHeight));
    // Back-left wheel
    painter.drawRect(QRectF(m_car.getX() + m_car.getWidth() - wheelWidth - 5, m_car.getY() - 3, wheelWidth, wheelHeight));
    // Back-right wheel
    painter.drawRect(QRectF(m_car.getX() + m_car.getWidth() - wheelWidth - 5, m_car.getY() + m_car.getHeight() - wheelHeight + 3, wheelWidth, wheelHeight));

    // Draw instructions text
    painter.setPen(Qt::white);
    painter.setFont(QFont("Arial", 12));
    painter.drawText(10, 25, "Use Arrow Keys to move the car");
    painter.drawText(10, 45, QString("Position: (%1, %2)").arg(static_cast<int>(m_car.getX())).arg(static_cast<int>(m_car.getY())));
}

void CarWindow::keyPressEvent(QKeyEvent *event)
{
    // Track pressed keys for smooth movement
    if (!event->isAutoRepeat()) {
        m_pressedKeys.insert(event->key());
    }
}

void CarWindow::keyReleaseEvent(QKeyEvent *event)
{
    // Remove released keys
    if (!event->isAutoRepeat()) {
        m_pressedKeys.remove(event->key());
    }
}

void CarWindow::updateState()
{
    // Handle all currently pressed keys for smooth diagonal movement
    if (m_pressedKeys.contains(Qt::Key_Up) || m_pressedKeys.contains(Qt::Key_W)) {
        m_car.moveUp();
    }
    if (m_pressedKeys.contains(Qt::Key_Down) || m_pressedKeys.contains(Qt::Key_S)) {
        m_car.moveDown();
    }
    if (m_pressedKeys.contains(Qt::Key_Left) || m_pressedKeys.contains(Qt::Key_A)) {
        m_car.moveLeft();
    }
    if (m_pressedKeys.contains(Qt::Key_Right) || m_pressedKeys.contains(Qt::Key_D)) {
        m_car.moveRight();
    }

    // Keep car within window bounds
    double x = m_car.getX();
    double y = m_car.getY();
    double w = m_car.getWidth();
    double h = m_car.getHeight();

    if (x < 0) m_car.setPosition(0, y);
    if (y < 0) m_car.setPosition(m_car.getX(), 0);
    if (x + w > WINDOW_WIDTH) m_car.setPosition(WINDOW_WIDTH - w, m_car.getY());
    if (y + h > WINDOW_HEIGHT) m_car.setPosition(m_car.getX(), WINDOW_HEIGHT - h);

    // Update car state
    m_car.update();

    // Trigger repaint
    update();
}
