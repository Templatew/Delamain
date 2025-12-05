/**
 * @file main.cpp
 * @brief Entry point for the CarSimQt application.
 * 
 * Creates a Qt application and displays the car simulation window.
 */

#include <QApplication>
#include "CarWindow.hpp"

int main(int argc, char *argv[])
{
    // Create Qt application
    QApplication app(argc, argv);

    // Create and show the main window
    CarWindow window;
    window.setWindowTitle("CarSimQt - Use Arrow Keys to Move");
    window.show();

    // Run the application event loop
    return app.exec();
}
