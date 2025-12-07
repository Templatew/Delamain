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

    QApplication app(argc, argv);

    CarWindow window;
    window.setWindowTitle("CarSimQt - Use Arrow Keys to Move");
    window.show();

    return app.exec();
}
