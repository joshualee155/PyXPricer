import numpy as np

def TriDiagSolver(a,b,c,y):
    """
    Uses Thomas algorithm for solving a tridiagonal matrix for n unknowns.
    a, b, and c are a list of the matrix entries
      Matrix form of:
      |b1 c1          | |x1]  |y1]
      |a2 b2 c2       | |x2|  |y2|
      |   a3 b3 c3    | |x3|= |y3|
      |               | |  |  |  |
      |           cn-1| |  |  |  |
      |         an bn | |xn|  |yn|
    """

    m = len(b)
    
    if len(a) != m - 1 or len(c) != m-1:
        print '>> Wrong index size for a in TriDiagSolver.\n'
        exit(1)

    # Calculate p and q
    c_prime = np.zeros(m)
    y_prime = np.zeros(m)
    c_prime[0] = c[0]/b[0]
    y_prime[0] = y[0]/b[0]
    
    c = np.append(c, 0.0)
    for j in range(1,m):
        c_prime[j] = c[j]/(b[j] - a[j-1] * c_prime[j-1])
        y_prime[j] = (y[j] - a[j-1] * y_prime[j-1])/(b[j] - a[j-1]* c_prime[j-1])
        
    x =  np.zeros(m)
    x[m-1] = y_prime[m-1]
    for i in range(m-2,-1,-1):
        x[i] = y_prime[i] - c_prime[i] * x[i+1]
    
    return x


def TriDiagMultVector(a,b,c,y):
    m = len(b)
    
    x =  np.zeros(m)
    for i in range(m):
        if i == 0:
            x[0] = b[0] * y[0] + c[0] * y[1]
        elif i == m-1:
            x[m-1] = a[m-2] * y[m-2] + b[m-1] * y[m-1]
        else:
            x[i] = a[i-1] * y[i-1] + b[i] * y[i] + c[i] * y[i+1]
            
    return x
'''
# Matrix
a= [3,1.5,4.5,4.5]
b= [-6,-4.5,-7.5,-7.5,-4.5] 
c= [3,3,3,3]
d= [0,0,100,0,0]
# Execute the function
x = thomas(a,b,c,d)
# Print the result
print x
[-16.666666666666664, -33.33333333333333, -33.33333333333333, -33.33333333333333, -33.33333333333333]
'''