#ifndef CARWINDOW_HPP
#define CARWINDOW_HPP

#include <QWidget>
#include <QTimer>
#include <QSet>
#include "Car.hpp"

/**
 * @class CarWindow
 * @brief Main window that displays and controls the car simulation.
 * 
 * Handles keyboard input, renders the car using QPainter,
 * and runs a game loop at approximately 60 FPS.
 */
class CarWindow : public QWidget
{
    Q_OBJECT

public:
    /**
     * @brief Construct a new CarWindow
     * @param parent Parent widget (optional)
     */
    explicit CarWindow(QWidget *parent = nullptr);
    ~CarWindow() override = default;

protected:
    /**
     * @brief Handle paint events to draw the car and background
     * @param event Paint event
     */
    void paintEvent(QPaintEvent *event) override;

    /**
     * @brief Handle key press events for car movement
     * @param event Key event
     */
    void keyPressEvent(QKeyEvent *event) override;

    /**
     * @brief Handle key release events
     * @param event Key event
     */
    void keyReleaseEvent(QKeyEvent *event) override;

private slots:
    /**
     * @brief Update game state (called by timer ~120 times per second)
     */
    void updateState();

private:
    Car m_car;                  ///< The car object
    QTimer m_timer;             ///< Timer for game loop
    QSet<int> m_pressedKeys;    ///< Set of currently pressed keys

    static constexpr int WINDOW_WIDTH = 800;
    static constexpr int WINDOW_HEIGHT = 600;
    static constexpr int TARGET_FPS = 120;
};

#endif // CARWINDOW_HPP
