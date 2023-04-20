import matplotlib.pyplot as plt

x = [i*2.5 for i in range(13)]
y_308 = [11.1, 10.5, 12.3, 8.8, 8.7, 9.6,
         10.9, 9.0, 9.5, 7.7, 12.2, 11.7, 11.1]
y_28 = [21.8, 11.5, 10.4, 12.7, 9.6, 7.7,
        8.9, 7.4, 9.4, 11.5, 12.2, 17.7, 12.4]
y_252 = [8.4, 8.5, 10.7, 6.7, 6.2, 6.1, 7.6, 6.0, 6.4, 6.1, 10.5, 9.4, 6.7]

plt.plot(x,y_308,'b*--')
plt.plot(x,y_28,'ro--')
plt.plot(x,y_252,'g^--')
plt.xlabel('Rotation of the pattern [°]')
plt.ylabel('Mean value of the error along the translations [%]')
plt.legend(['9/10 of p','10/10 of p','11/10 of p'])
plt.ylim(bottom=0.0)
plt.tight_layout()
plt.show()
