import Gnuplot
import numpy as np
import math
import time

def plot(agent):
  g=Gnuplot.Gnuplot()
  g('set xrange [-400.0: 400.0]')
  g('set yrange [-400.0: 400.0]')
  g('set pm3d')
  g('set view map')
  g('unset key')
  g('set size square')

  g('unset arrow')
  # g('set arrow from 0, 0 to -150, 0 nohead front lt 3')
  # g('set arrow from -150, 0 to -150, -50 nohead front lt 3')
  # g('set arrow from -150, -50 to 0, -50 nohead front lt 3')
  # g('set arrow from 0, -50 to 0, 0 nohead front lt 3')
  # g('set arrow from 200, 100 to 200, 330 nohead front lt 3')
  # g('set arrow from 200, 330 to 300, 330 nohead front lt 3')
  # g('set arrow from 300, 330 to 300, 100 nohead front lt 3')
  # g('set arrow from 300, 100 to 200, 100 nohead front lt 3')

  # What color scheme to use
  # see http://gnuplot.sourceforge.net/demo_4.0/pm3dcolors.html
  #set palette gray
  # g('set palette color')
  #set palette model XYZ functions gray**0.35, gray**0.5, gray**0.8
  g('set palette model RGB functions 1-gray, 1-gray, 1-gray')

  # How fine the plotting should be, at some processing cost:
  g('set isosamples 100')
  #set isosamples 30
  sigma_t = agent.sigma_t
  mu=agent.mu
  sigma_x = sigma_t[0,0]
  sigma_y = sigma_t[3,3]
  rho = sigma_t[0,3]/(sigma_x*sigma_y)
  x=mu[0,0]
  y=mu[3,0]
  # x=200
  # y=300
  # print "sigma_x: "+str(sigma_x)
  # print "sigma_y: "+str(sigma_y)
  # g.splot('1.0/(2.0 * pi * '+str(sigma_x)+' * '+str(sigma_y)+' * sqrt(1 - '+str(rho)+'**2)) \
  # * exp(-1.0/2.0 * ('+str(x)+'**2 / '+str(sigma_x)+'**2 + '+str(y)+'**2 / '+str(sigma_y)+'**2 \
  # - 2.0*'+str(rho)+'*'+str(x)+'*'+str(y)+'/('+str(sigma_x)+'*'+str(sigma_y)+')))')
  g.splot('1.0/(2.0 * pi * '+str(sigma_x)+' * '+str(sigma_y)+' * sqrt(1 - '+str(rho)+'**2)) \
  * exp(-1.0/2.0 * (('+str(x)+'-x)**2 / '+str(sigma_x)+'**2 + ('+str(y)+'-y)**2 / '+str(sigma_y)+'**2 \
  - 2.0*'+str(rho)+'*('+str(x)+'-x)*('+str(y)+'-y)/('+str(sigma_x)+'*'+str(sigma_y)+'))) with pm3d')
  secondsToSeePlot=15
  time.sleep(secondsToSeePlot)
  return secondsToSeePlot