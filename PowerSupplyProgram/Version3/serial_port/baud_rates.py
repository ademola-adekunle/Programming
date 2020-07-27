import termios

BAUD_RATES = {'50':termios.B50,
              '75':termios.B75,
              '110':termios.B110,
              '134':termios.B134,
              '150':termios.B150,
              '200':termios.B200,
              '300':termios.B300,
              '600':termios.B600,
              '1200':termios.B1200,
              '1800':termios.B1800,
              '2400':termios.B2400,
              '4800':termios.B4800,
              '9600':termios.B9600,
              '19200':termios.B19200,
              '38400':termios.B38400,
              '57600':termios.B57600,
              '115200':termios.B115200,
              '230400':termios.B230400,
              '460800':termios.B460800}

RATE_SELECTION = ('50', '75', '110', '134', '150', '200', '300', '600', '1200',
                  '1800', '2400', '4800', '9600', '19200', '38400', '57600',
                  '115200', '230400', '460800')
