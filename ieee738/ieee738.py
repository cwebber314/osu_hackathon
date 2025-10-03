"""Python implementation for Calcualting the Current-Temperature Relationship
of Bare Overhead Conductors.

References
--------------
[1] ieee738-2006 spec
     
"""
import math as m
from datetime import datetime
import logging
import pdb
from pydantic import BaseModel, Field
from typing import Literal, Optional

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Logging init")

def polyval(p, x):
    result = 0
    N = len(p)
    for i in range(N):
        result += p[i] * x**(N-i-1)
    return result

def rad2deg(rad):
    return rad*180.0/m.pi

def deg2rad(deg):
    return deg*m.pi/180.0

class ConductorParams(BaseModel):
    # Ambient Params 
    Ta: float = Field(description="Ambient temperature in deg C")
    WindVelocity: float = Field(description="Wind Velocity in ft/sec")
    WindAngleDeg: float = Field(description="Wind angle in degrees between 0 and 90")
    Elevation: float = Field(description="Height above sea level. units ft")
    Latitude: float = Field(description="Latitude in degrees")
    SunTime: float = Field(description="hour of day. Between 0-24")
    Emissivity: float = Field(description="Emissivity. Between 0-1.")
    Absorptivity: float = Field(description="Absorptivity. Between 0-1.")
    Direction: Literal['EastWest', 'NorthSouth'] = Field(description='Orientation of conductor')
    Atmosphere: Literal['Clear', 'Industrial'] = Field(description='Atmosphere')
    Date: Optional[str] = Field(default='12 Jun', description='Day of year in format')

    # Properties of the conductor
    Tc: float = Field(description="Temperature of conductor used to calculate the flow. This is typically the max allowable temperature of the conductor.")
    Diameter: float = Field(description="Conductor Diameter. Units inches")
    TLo: float = Field(description="Temperature of Resistance specified in RLo")
    RLo: float = Field(description="Resistance at temperature TLo. Units ohms/ft")
    THi: float = Field(description="Temperature of Resistance specified in RHi")
    RHi: float = Field(description="Resistance at temperature THi. Units ohms/ft")
    ConductorsPerBundle: Optional[int] = Field(default=1, description='Number of conductors in the bundle')

class Conductor:
    """IEEE738-2012 calculation with US units
    """
    def __init__(self, params: ConductorParams):
        # Assign all 
        for name, val in params:
            setattr(self, name, val)

        # Internal params which user might care about. 
        # These are the terms of the classic heat balance equation
        self.qs = None
        self.qr = None
        self.qc = None

    def set_cond_params(self, d):
        """Import conductor parameters from a dict
        """
        self.RLo = d.get('RLo_mi') / 5280.0
        self.RHi = d.get('RHi_mi') / 5280.0
        # self.Tc = d.get('Tc')

    def forced_convection_heat_loss(self):
        """Calculate Forced Convection Heat Loss

        D: Outer Diameter of Conductor (in)
        pf: density of Air (lb/ft^3)
        Vwind: Velocity of air stream (ft/h)
        uf: absolute viscosity of air (lb/ft*hr)
        kf: thermal conductivity of air at temperature Tfilm(degC) (W/ft) 
        """
        D = self.Diameter

        # Wind velocity in ft/hr for this calculation
        Vwind = self.WindVelocity * 60.0 * 60.0

        # Airfilm temperature
        Hc = self.get_hc()
        pf = self.get_pf()
        uf = self.get_uf()
        kf = self.get_kf()

        qc1 = (1.01 + 0.371*((D*pf*Vwind)/uf)**0.52) * kf * (self.Tc - self.Ta)
        qc2 = 0.1695*(D*pf*Vwind/uf)**0.6 * kf *(self.Tc - self.Ta)
        # Kangle: Wind direction factor
        w = deg2rad(90 - self.WindAngleDeg)
        Kangle = 1.194 - m.sin(w) - 0.194*m.cos(2*w) + 0.368*m.sin(2*w)

        qc = max(qc1*Kangle, qc2*Kangle)

        logger.debug("Forced Convection Heat Loss")
        logger.debug("----------------------------")
        logger.debug("D = %s" % D)
        logger.debug("Vw = %s" % Vwind)
        logger.debug("WindAngleDeg = %s" % self.WindAngleDeg)
        logger.debug("Kangle = %s" % Kangle)
        logger.debug("uf = %s" % uf)
        logger.debug("pf = %s" % pf)
        logger.debug("kf = %s" % kf)
        logger.debug("qc1 = %s" % qc1)
        logger.debug("qc1*Kangle = %s" % (qc1*Kangle))
        logger.debug("qc2 = %s" % qc2)
        logger.debug("qc2*Kangle = %s" % (qc2*Kangle)) 
        return qc

    def get_uf(self):
        """
        Dynamic Viscosity of Air
        """
        Tfilm = (self.Tc + self.Ta) / 2.0
        uf = (0.00353*(Tfilm + 273.0)**1.5) / (Tfilm + 383.4)
        return uf

    def get_pf(self):
        """
        Section 2.5.2 Density (table1)
        Density of Air (lb/ft^3)
        Hc == Altitude of sun (degrees)
        He == Elevation
        
        pf = f(Tfilm, Elevation)

        The ieee738-1993 spec is inconsistent.  The qbasic uses elevation
        and the formula uses Hc.  Using Table1 to check formula, we see that 
        Elevation should be used instead of altitude of sun.
        """
        Tfilm = (self.Tc + self.Ta) / 2.0
        He = self.Elevation
        pf = (0.080695 - 2.901e-6*He + 3.7e-11*He**2) / (1 + 0.00367*Tfilm)

        logger.debug("pf.  Density of air")
        logger.debug("-----------------------")
        logger.debug("Tc: %s" % self.Tc)
        logger.debug("Ta: %s" % self.Ta)
        logger.debug("Tfilm: %s" % Tfilm)
        logger.debug("He: %s" % He)
        logger.debug("pf: %s" % pf)

        return pf

    def get_kf(self):
        """
        Calculate kf in W/ft (degC)
        thermal conductivity of air at temperature Tfilm 
        Calculated from Table1
        """
        Tfilm = (self.Tc + self.Ta) / 2.0
        p = [7.388e-3, 2.279e-5, -1.343e-9]
        p = p[::-1]
        pf = polyval(p, Tfilm)
        # pf in W/(ft-degC)
        return pf

    def natural_convection_heat_loss(self):
        """
        Calculate natural convection heat loss
        """
        Hc = self.get_hc()
        pf = self.get_pf()

        # you can hit this case in temperature sweeps where the ambient
        # temperature is greater than the max rating.  
        if self.Tc - self.Ta < 0:
            logger.debug("WARNING: Tc < Ta.  Settings Tc = Ta + 0.1")
            self.Tc = self.Ta + 0.1

        qc = 0.283 * pf**0.5 * self.Diameter**0.75 * (self.Tc-self.Ta)**1.25
        
        logger.debug("Natural Convection Heat Loss")
        logger.debug("-----------------------------")
        logger.debug("Hc = %s" % Hc)
        logger.debug("pf = %s" % pf)
        logger.debug("qc = %s" % qc) 

        return qc

    def convection_heat_loss(self):
        """Get Convection Heat loss (qc)
        """
        qcn = self.natural_convection_heat_loss()
        qcf = self.forced_convection_heat_loss()
        qc = max(qcn, qcf)
        logger.debug("qc. Convection Heat Loss")
        logger.debug("----------------------------")
        logger.debug("qcn: %s" % qcn)
        logger.debug("qcf: %s" % qcf)
        logger.debug("qc: %s" % qc)

        return qc

    def radiated_heat_loss(self):
        """
        qr: Radiated heat loss
        """
        qr = 0.138 * self.Diameter * self.Emissivity * \
            ( ((self.Tc + 273.0)/100.0)**4 - ((self.Ta+273.0)/100.0)**4 )  

        logger.debug("qr. Radiated Heat Loss")
        logger.debug("------------------------")
        logger.debug("Tc: %s" % self.Tc)
        logger.debug("Ta: %s" % self.Ta)
        logger.debug("D: %s" % self.Diameter)
        logger.debug("E: %s" % self.Emissivity)
        logger.debug("qr: %s" % qr)
        return qr

    def get_hc(self):
        """
        Get Altitude of sun (degrees).  Equation 15.
        """
        # d = solar declination 
        # lat = degrees latitude
        # w = hour angle.  The number of hours from noon * 15deg
        # Number of days into the year

        year_day1 = datetime.strptime('1 Jan', "%d %b")
        day = datetime.strptime(self.Date, "%d %b")
        N = (day - year_day1).days
        w = (self.SunTime-12.0) * 15.0
        d = 23.4583*m.sin(deg2rad((284.0+N)/365.0 * 360.0))
        lat = self.Latitude

        Hc = m.asin(m.cos(deg2rad(lat))*m.cos(deg2rad(d))*m.cos(deg2rad(w)) + m.sin(deg2rad(lat))*m.sin(deg2rad(d)))
        Hc = Hc*180.0/m.pi

        logger.debug("Hc Calculation. Altitude of the sun")
        logger.debug("------------------------------------")
        logger.debug("SunTime: %s" % self.SunTime)
        logger.debug("Latitude: %s" % self.Latitude)
        logger.debug("N (Number of days into year): %s" % N)
        logger.debug("d (solar declination degrees): %s" % d) 
        logger.debug("Hc: %s" % Hc)

        self.solar_declination = d
        self.hour_angle = w
        return Hc

    def elevation_correction(self):
        """
        Elevation Correction for Qs
        """
        p = [1.0, 3.5e-5, -1.0e-9]
        p = p[::-1]
        Ke = polyval(p, self.Elevation)
        
        logger.debug("Elevation Correction")
        logger.debug("---------------------")
        logger.debug("He: %s" % self.Elevation)
        logger.debug("Ke: %s" % Ke)

        return Ke

    def get_Qs(self, Hc):
        """Calculate Qs.  Total heat flux received by a surface at sea level 
        normal to the sun's rays
        
        input: 
            - Hc(float): Solar Altitude Hc (degrees)
        """
        if self.Atmosphere == 'Clear': #0
            # Solar Heating at earch surface (W/ft^2) in clear air
            p = [-3.9241, 
                 5.9276, 
                 -1.7856e-1, 
                 3.223e-3, 
                 -3.3549e-5, 
                 1.8053e-7, 
                 -3.7868e-10] 
        elif self.Atmosphere == 'Industrial': #1
            # Solar Heating at earch surface (W/ft^2) in industrial air
            p = [4.9408, 
                 1.3202, 
                 6.1444e-2,
                 -2.9411e-3, 
                 5.07752e-5, 
                 -4.03627e-7,
                 1.22967e-9]
        else:
            logger.debug("ERROR: Invalid Atmosphere %s" % self.Atmosphere)
            logger.debug("Expecting 'Clear' or 'Industrial'")
            logger.debug()

        p = p[::-1]
        Qs = polyval(p, Hc)

        logger.debug("Qs")
        logger.debug("----")
        logger.debug("atmostphere: %s" % self.Atmosphere)
        logger.debug("Hc: %s" % Hc)
        logger.debug("Qs: %s" % Qs)

        return Qs

    def get_zc(self):
        """
        Azimuth of Sun
        """
        lat = self.Latitude
        w = self.hour_angle
        d = self.solar_declination
        logger.debug("Zc Azimuth of Sun. Solar azimuth angle")
        logger.debug("--------------------------------------")
        logger.debug("lat: %s" % self.Latitude)
        logger.debug("d: %s" % self.solar_declination)
        logger.debug("w: %s" % self.hour_angle)

        X = m.sin(deg2rad(w)) / (m.sin(deg2rad(lat))*m.cos(deg2rad(w)) - 
                               m.cos(deg2rad(lat))*m.tan(deg2rad(d)) )
        
        logger.debug("X (solar azimuth variable): %s" % X)

        # Table 3 - Solar azimuth constant C
        if w >= -180 and w < 0:
            if X >= 0:
                C = 0
            else:
                C = 180
        elif w >= 0 and w <= 180:
            if X >= 0:
                C = 180
            else:
                C = 360
        else:
            logger.debug("ERROR: I can't figure out C in the Zc calculation")

        # Zc is in degrees
        Zc = C + rad2deg(m.atan(X))

        logger.debug("C (solar azimuth constant): %s" % C)
        logger.debug("Zc (degrees): %s" % Zc)
        return Zc

    def solar_heat_gain(self):
        """
        qs: Calculate Solar Heat Gain
        
        qs = f(Latitude, Direction(E/W vs N/S)) 
        """
        Hc = self.get_hc()
        Qs = self.get_Qs(Hc)
        Zc = self.get_zc()

        if self.Direction == 'NorthSouth': #0
            z1 = 0.0
        elif self.Direction == 'EastWest': #1
            z1 = 90.0
        else:
            logger.debug("ERROR: Unknown Direction %s" % self.Direction)
            logger.debug("Valid values: 'NorthSouth' OR 'EastWest'")

        # h3 == Hc.  Altitude of sun in degrees
        # z4 == Zc.  Azimuth of sun in degrees
        e1 = m.cos(deg2rad(Hc)) * m.cos(deg2rad(Zc-z1))

        theta = m.acos(e1) # the old basic didn't have inverse cosine
        thetaDeg = rad2deg(theta)

        # absorp == a (alpha)
        # Elevation correction 
        A = self.Diameter / 12.0
        qs = self.Absorptivity * Qs * m.sin(theta) * A * \
             (1.0 + 3.5e-5*self.Elevation - 1.0e-9 * self.Elevation**2)

        logger.debug("qs. Solar Heat Gain")
        logger.debug("---------------------")
        logger.debug("Direction: %s" % self.Direction)
        logger.debug("Hc: %s" % Hc)
        logger.debug("Zc: %s" % Zc)
        logger.debug("z1: %s" % z1)
        logger.debug("alpha (Absorptivity): %s" % self.Absorptivity)
        logger.debug("theta: %s" % theta)
        logger.debug("thetaDeg: %s" % thetaDeg)
        logger.debug("A: %s" % A)
        logger.debug("Qs (W/ft^2): %s" % Qs)
        logger.debug("qs (W/ft): %s" % qs)
        return qs

    def get_res_Tc(self):
        logger.debug("R(Tc)")
        logger.debug("------")
        logger.debug("RLo: %s" % self.RLo)
        logger.debug("TLo: %s" % self.TLo)
        logger.debug("RHi: %s" % self.RHi)
        logger.debug("RLo: %s" % self.THi)

        rTc = self.RLo + ((self.RHi - self.RLo) / \
                (self.THi - self.TLo))*(self.Tc - self.TLo)

        logger.debug("R(Tc): %s" % rTc)
        return rTc

    def input_validation(self):
        """Check input parameter for data type and other problems.
        TODO: This should just be part of the pydantic definition
        """
        params = ('Diameter', 'Direction', 'RLo', 'RHi', 'TLo', 'THi', 'WindVelocity',
                'WindAngleDeg', 'Direction', 'Elevation', 'Latitude', 'SunTime' )
        for a in params:
            if not hasattr(self, a):
                raise KeyError("Parameter not defined: {}".format(a))

        if self.RLo > 0.001:
            raise ValueError("RLo is much higher than expectged.  Units should be Ohms/ft.")
        if self.RHi > 0.001:
            raise ValueError("RLo is much higher than expected.  Units should be Ohms/ft.")
        if self.Absorptivity < 0:
            raise ValueError("Absorptivity out of range.")
        if self.Emissivity < 0:
            raise ValueError("Emissivity is out of range.")

    def steady_state_thermal_rating(self):
        """Conductor rating in Amps

        Args:
          - None
        Returns:
          - float: rating of conductor in amps
        """
        self.input_validation()
        qc = self.convection_heat_loss()
        qs = self.solar_heat_gain()
        qr = self.radiated_heat_loss()
        rTc = self.get_res_Tc()

        if qs == 0:
            raise ValueError("Qs (solar heat gain) is zero.  Something went wrong in the calculation")
        if qr == 0:
            raise ValueError("Qr (radiated heat loss) is zero.  Something went wrong in the calculation")

        # Consider the case where qc + qr - qs < 0
        # you can't take the sqrt of a negative

        if qc + qr - qs < 0:
            I = 0
        else:
            I = m.sqrt((qc + qr - qs)/rTc)
            
        self.qc = qc
        self.qs = qs
        self.qr = qr

        # pdb.set_trace()
        I_bundled = I * self.ConductorsPerBundle
        logger.debug("Steady State Thermal Rating")
        logger.debug("-----------------------------")
        logger.debug("qc: %s" % qc)
        logger.debug("qr: %s" % qr)
        logger.debug("qs: %s" % qs)
        logger.debug("R(Tc): %s" % rTc)
        logger.debug("I: %s" % I)
        logger.debug("I for bundles: %s" % I_bundled)
        return I_bundled

    def qs(self):
        "Get solar heat gain from the last calculation"
        return self.qs

    def qr(self):
        "Get radiated head loss from the last calculation"
        return self.qr
    
    def qc(self):
        "Get Natural/convective cooling from the last calculation"
        return self.qc