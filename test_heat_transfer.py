import heat_transfer as ht
import pprint
import unittest

pp = pprint.PrettyPrinter()

ureg = ht.ureg
Q_ = ht.Q_


class RefPropTest(unittest.TestCase):
    """Verify fluid properties are calculated accurately.

    Tests borrowed from pyrefprop package.
    """

    criteria = 0.00001  # NIST acceptance criteria

    def assertNIST(self, nist, calc, criteria=None):
        criteria = criteria or self.criteria
        assert abs(nist-calc) / nist < criteria, \
            f'Calculated value {calc} is not within {criteria:%} of NIST value {nist}'

    def test_air(self):
        fluid = ht.ThermState('air.mix', backend='REFPROP')
        self.assertNIST(fluid.M.magnitude, 28.958600656)
        # TODO Open an issue with CoolProp

    def test_argon(self):
        fluid = ht.ThermState('argon', backend='REFPROP')
        P = 2 * 1000 * ureg.kPa
        D = 15 / fluid.M * ureg.mol/ureg.L
        fluid.update_kw(P=P, Dmolar=D)
        self.assertNIST(637.377588657857, fluid.T.to(ureg.K).magnitude)

    def test_r134a(self):
        fluid = ht.ThermState('r134a', backend='REFPROP')
        T = 400 * ureg.K
        D = 50 / fluid.M * ureg.mol/ureg.L
        fluid.update_kw(T=T, Dmolar=D)
        self.assertNIST(1.45691892789737, fluid.P.to(ureg.kPa).magnitude/1000)

    def test_oxygen(self):
        fluid = ht.ThermState('oxygen', backend='REFPROP')
        T = 100 * ureg.K
        P = 1000 * ureg.kPa
        fluid.update_kw(T=T, P=P)
        self.assertNIST(153.886680663753,
                        fluid.viscosity.to(ureg.uPa*ureg.s).magnitude)

    def test_nitrogen(self):
        fluid = ht.ThermState('nitrogen', backend='REFPROP')
        T = 100 * ureg.K
        fluid.update_kw(T=T, Q=0)
        self.assertNIST(100.111748964945,
                        fluid.conductivity.to(ureg.W/(ureg.m*ureg.K)).magnitude*1000)

    def test_air_density(self):
        fluid = ht.ThermState('air.mix', backend='REFPROP')
        T = (((70 - 32) * 5 / 9) + 273.15) * ureg.K
        P = 14.7 / 14.50377377 * (10**5) / 1000 * ureg.kPa
        fluid.update_kw(P=P, T=T)
        self.assertNIST(0.0749156384666842,
                        fluid.Dmolar.to(ureg.mol/ureg.L).magnitude*fluid.M*0.062427974)

    # def test_freon_mixture(self):
    #     fluid = ht.ThermState('R32&R125', backend='REFPROP')
    #     fluid.set_mole_fractions(0.3, 0.7)
    #     P = 10 * 1000 * ureg.kPa
    #     Smolar = 110 * ureg.J / (ureg.mol * ureg.K)
    #     fluid.update_kw(P=P, Smolar=Smolar)
    #     self.assertNIST(23643.993624382,
    #                     fluid.Hmolar.to(ureg.J/ureg.mol).magnitude)
    # TODO Figure out the issue with mixtures (possibly refprop_setref/ixflag thing)

    # def test_ethane_butane(self):
    #     fluid = ht.ThermState('ethane&butane', backend='REFPROP')
    #     fluid.set_mole_fractions(0.5, 0.5)
    #     Dmolar = 30 * 0.45359237 / 0.028316846592 / fluid.M * ureg.mol / ureg.L
    #     Hmolar = 283 * 1.05435026448889 / 0.45359237 * fluid.M * ureg.J / ureg.mol
    #     fluid.update_kw(Dmolar=Dmolar, Hmolar=Hmolar)
    #     self.assertNIST(298.431320311048,
    #                     fluid.T.to(ureg.degF).magnitude)
    # TODO Figure out the issue with mixtures (possibly refprop_setref/ixflag thing)

    def test_ammonia_water(self):
        fluid = ht.ThermState('ammonia&water', backend='REFPROP')
        fluid.set_mole_fractions(0.4, 0.6)
        T = (((300 - 32) * 5 / 9) + 273.15) * ureg.K
        P = 10000 / 14.50377377 * (10**5) / 1000 * ureg.kPa
        fluid.update_kw(T=T, P=P)
        self.assertNIST(5536.79144924071,
                        fluid.speed_sound.to(ureg.m/ureg.s).magnitude * 1000 / 25.4 / 12)

    def test_octane(self):
        fluid = ht.ThermState('octane', backend='REFPROP')
        T = (100+273.15) * ureg.K
        fluid.update_kw(T=T, Q=0)
        self.assertNIST(319.167499870568,
                        fluid.latent_heat.to(ureg.J/ureg.g).magnitude)

    def test_R410A_mole_fraction(self):
        fluid = ht.ThermState('R410A.MIX', backend='REFPROP')
        self.assertNIST(0.697614699375863,
                        fluid.mole_fractions[0])

    def test_R410A_mass_fraction(self):
        fluid = ht.ThermState('R410A.MIX', backend='REFPROP')
        self.assertNIST(0.5,
                        fluid.mass_fractions[0])


class FunctionsTest(unittest.TestCase):
    def test_rad_hl_1(self):
        eps = 0.02
        T1 = 27 * ureg.degC
        T2 = -183 * ureg.degC
        A = 0.05 * ureg.m**2
        heat_flow = abs(ht.rad_hl(T1, eps, T2, eps)) * A
        self.assertAlmostEqual(0.23054, heat_flow.to(ureg.W).magnitude, 5)

    def test_rad_hl_2(self):
        eps = 0.55
        T1 = 27 * ureg.degC
        T2 = -183 * ureg.degC
        A = 0.05 * ureg.m**2
        heat_flow = abs(ht.rad_hl(T1, eps, T2, eps)) * A
        self.assertAlmostEqual(8.65727, heat_flow.to(ureg.W).magnitude, 5)

    def test_rad_hl_3(self):
        eps = 0.8
        T1 = 327 * ureg.degC
        T2 = 127 * ureg.degC
        eps_b = 0.05
        heat_flow = abs(ht.rad_hl(T1, eps, T2, eps,
                                  baffles={'N': 1, 'eps': eps_b}))
        self.assertAlmostEqual(145.7373,
                               heat_flow.to(ureg.W/ureg.m**2).magnitude, 5)

    def test_rad_hl_4(self):
        T1 = 327 * ureg.degC
        eps_1 = 0.8
        T2 = 127 * ureg.degC
        eps_2 = 0.4
        eps_b = 0.05
        heat_flow = abs(ht.rad_hl(T1, eps_1, T2, eps_2,
                                  baffles={'N': 1, 'eps': eps_b}))
        self.assertAlmostEqual(141.37391,
                               heat_flow.to(ureg.W/ureg.m**2).magnitude, 5)


class PipingTest(unittest.TestCase):
    """Simple piping check to see if basic functionality works.

    Doesn't check for correctness yet."""

    def assertApproxEqual(self, data, calc, uncertainty=0.1):
        assert abs(data-calc) / data < uncertainty, \
            f'Calculated value {calc} is not within {uncertainty:.1%} of data value {data}'

    def test_create_pipes(self):
        tube = ht.piping.Tube(Q_('1 inch'))
        pipe = ht.piping.Pipe(Q_('1 inch'))
        c_tube = ht.piping.CopperTube(Q_('3/4 inch'))
        vj_pipe = ht.piping.VJPipe(Q_('1 inch'), VJ_D=Q_('2 inch'))
        corr_pipe = ht.piping.CorrugatedPipe(Q_('1 inch'))
        entrance = ht.piping.Entrance(Q_('1 inch'))
        pipe_exit = ht.piping.Exit(Q_('1 inch'))
        orifice = ht.piping.Orifice(Q_('1 inch'))
        c_orifice = ht.piping.ConicOrifice(1, Q_('3/4 inch'))
        annulus = ht.piping.Annulus(Q_('1 inch'), Q_('3/4 inch'))
        pipe_elbow = ht.piping.PipeElbow(Q_('1 inch'), N=2)
        elbow = ht.piping.Elbow(Q_('1 inch'), N=2)
        pipe_tee = ht.piping.PipeTee(Q_('1 inch'), N=2)
        tee = ht.piping.Tee(Q_('1 inch'), N=2)
        valve = ht.piping.Valve(Q_('1 inch'), 1)
        # g_valve = ht.piping.GlobeValve(Q_('1 inch'))
        # print(f'Generated {g_valve}')
        # v_cone = ht.piping.VCone(Q_('1 inch'), 0.7, 1)
        # print(f'Generated {v_cone}')
        cont = ht.piping.Contraction(pipe, tube)
        enl = ht.piping.Enlargement(tube, pipe)
        test_state = ht.ThermState('air', P=ht.P_NTP, T=ht.T_NTP)
        piping = ht.piping.Piping(
            test_state,
            [pipe, vj_pipe, corr_pipe, entrance, pipe_exit, orifice, c_orifice,
             tube, c_tube, annulus, pipe_elbow, elbow, pipe_tee, tee, valve,
             # g_valve, v_cone,
             cont, enl])
        piping.volume()
        self.assertApproxEqual(21.2*ureg.psi, piping.dP(Q_('10 g/s')))

    def test_f_Darcy(self):
        eps_smooth = 0.0018 * ureg.inch
        Re = 1e8
        ID = 0.2 * ureg.inch
        eps_r = eps_smooth/ID
        self.assertApproxEqual(0.0368, ht.piping.f_Darcy(Re, eps_r))
        ID = 0.4 * ureg.inch
        eps_r = eps_smooth/ID
        self.assertApproxEqual(0.0296, ht.piping.f_Darcy(Re, eps_r))
        ID = 1 * ureg.inch
        eps_r = eps_smooth/ID
        self.assertApproxEqual(0.0228, ht.piping.f_Darcy(Re, eps_r))
        ID = 2 * ureg.inch
        eps_r = eps_smooth/ID
        self.assertApproxEqual(0.0191, ht.piping.f_Darcy(Re, eps_r))
        eps_r = 0.006
        Re = 1e5
        self.assertApproxEqual(0.033, ht.piping.f_Darcy(Re, eps_r))
        eps_r = 0.006
        Re = 1e3
        self.assertApproxEqual(64/Re, ht.piping.f_Darcy(Re, eps_r))

    # def test_Crane_4_22(self):
    #     test_air = ht.ThermState('air', P=2.343*ureg.bar, T=40*ureg.degC)
    #     pipe = ht.piping.Pipe(1/2, SCH=80, L=3*ureg.m)
    #     piping = ht.piping.Piping(
    #         test_air,
    #         [pipe,
    #          ht.piping.Exit(pipe.ID)])
    #     Y = 0.76  # Taken from Crane; temporary stub
    #     flow = ht.to_standard_flow(piping.m_dot(), test_air) * Y
    #     # TODO Check this test (might have to do with subsonic flow)
    #     self.assertAlmostEqual(1.76, flow.to(ureg.m**3/ureg.min).magnitude)

    def test_Crane_7_16(self):
        air = ht.ThermState('air', P=65*ureg.psig, T=110*ureg.degF)
        pipe = ht.piping.Pipe(1, SCH=40, L=75*ureg.ft)
        flow = 100 * ureg.ft**3/ureg.min
        m_dot = flow * ht.Air.Dmass
        piping = ht.piping.Piping(
            air,
            [pipe, ht.piping.Exit(pipe.ID)])
        self.assertApproxEqual(2.61, piping.dP(m_dot).m_as(ureg.psi))

# TODO Add Crane examples: 4-22 (may need Y implementation),
# 4-20, 4-19, 4-18, 4-16, 4-12?, 4-10?


class CPWrapperTest(unittest.TestCase):
    """Test for additional methods of ThermState class"""
    def test_copy(self):
        """Minimal test of copy method"""
        test_state = ht.ThermState('nitrogen')
        test_state.copy()
        test_state.update_kw(T=300*ureg.K, P=1*ureg.MPa)
        test_state.copy()



if __name__ == '__main__':
    unittest.main()

    # print('\nCalculating evaporation heat')
    # Test_State.update('T', Q_('4.2 K'), 'Q', Q_('0'))
    # Hmass_liq = Test_State.Hmass
    # print(Hmass_liq)
    # print(Test_State.specific_heat_input)
    # Test_State.update('T', Q_('4.2 K'), 'Q', Q_('1'))
    # Hmass_vap = Test_State.Hmass
    # print(Hmass_vap)
    # Hmass_evap = Hmass_vap - Hmass_liq
    # print(Hmass_evap)
    # print(Test_State.specific_heat_input)
    # Test_State.update('P', P_SHI, 'T', Q_('200 K'))
    # print(theta_bruce(Test_State.P).to(ht.ureg.J/ht.ureg.kg), T_SHI.to(ht.ureg.K))
    # print(ht.theta_heat(Test_State))
    # TestPipe = ht.piping.Pipe(1, SCH=10, L=Q_('1 m'))
    # print(TestPipe.update(S=Q_('16700 psi'), E=0.8, W=1, Y=0.4))
    # print(TestPipe.pressure_design_thick(ht.P_NTP))
    # TestPipe2 = ht.piping.Pipe(0.25)
    # print(TestPipe2.update(S=Q_('1000 psi'), E=1, W=1, Y=0.4))
    # TestPipe.branch_reinforcement(TestPipe2, 10*ht.P_NTP)
    # print(TestPipe.pressure_design_thick(Q_('305 psig')).to(ht.ureg.inch))
    # print(TestPipe.volume.to(ht.ureg.ft**3))
# print()
# # TODO Check m_dot and P_in methods
# # print(TestPiping.volume)
# # pp.pprint(ht.piping.NPS_table)

# print('Testing mean of nist curve fit')
# T0 = 300 * ureg.K
# T1 = 100 * ureg.K
# T2 = 200 * ureg.K
# T4 = 5 * ureg.K
# print(ht.nist_property('304SS', 'TC', T1))  # Was 9
# print(ht.nist_property('304SS', 'TC', T1, T2))  # Was 11
# print(ht.nist_property('OFHC', 'EC', T0))  # 1.65e-5
# print(ht.nist_property('304SS', 'LE', 150*ureg.K))  # -2e-3



# #print(ht.Gr(Test_State, Q_('300 K'), Q_('1 m')))
# #Test_pipe = ht.piping.Pipe(1/8, L=ht.ureg('1 m'))
# #print(Test_pipe)
# #Test_piping = ht.piping.Piping(ht.Air, [Test_pipe])
# #print(Test_piping.m_dot(P_out = ht.piping.ureg('1 psi')))
# #PipingFluid = ht.ThermState('air')
# #PipingFluid.update('P', 1*ht.ureg.atm, 'T', 38*ht.ureg.degC)
# #print ("""100 SCFM of air is equivalent to {:.3g} of Nitrogen flow for P = 1 atm
# #       and T = 38 C.""".format(ht.from_scfma(100*ht.ureg('ft^3/min'), PipingFluid)))
# #print ("CGA S-1.3 Formula from 6.1.4 a) gives 0.0547 kg/s for the same air capacity.")
# #Re = ht.Re(PipingFluid, ht.ureg('1g/s'), ht.ureg('5 mm'))
# #print(Re)
# #theta_temp = ht.theta_temp(ht.ureg('100 K'), ht.ureg('300 K'), ht.ureg('77 K'))
# #Bi = ht.Bi(ht.ureg('1 W/(m*K)'), ht.ureg('1 cm'), ht.ureg('10 W/(m**2*K)'))
# #Fo = ht.Fo_cyl(theta_temp, Bi)
# #print(f'Biot number is: {Bi:.3}')
# #print(f'Fourier number is: {Fo:.3}')
# #G10_sc = [-2.4083, 7.6006, -8.2982, 7.3301, -4.2386, 1.4294, -0.24396, 0.015236, 0]
# #G10_tc = [-4.1236, 13.788, -26.088, 26.272, -14.663, 4.4954, -0.6905, 0.0397, 0] #normal direction
# #print(ht.nist_curve_fit(300, G10_tc))
# #print(quad(lambda x: ht.nist_curve_fit(x, G10_tc ), 77, 300)[0]/(77-300))
# #
# #print('\nTesting invert dP calc')
# #m_dot = ht.ureg('1000 g/s')
# #P_out = ht.ureg('0 psig')
# #Test_piping.P_in(m_dot, P_out)
# #print(Test_piping.Fluid.P.to(ht.ureg.psig))
# ##for p in range(1,100,10):
# ##    m_dot = ht.ureg('1 g/s')
# ##    P_test = Q_(p, ht.ureg.psig)
# ##    Test_piping.init_cond['fluid'] = 'helium'
# ##    Test_piping.init_cond['P'] = P_test
# ##    T_test = ht.max_theta(Test_piping.init_cond)
# ##    Test_piping.init_cond['T'] = T_test
# ##    print(Test_piping.init_cond['P'].to(ht.ureg.psig), Test_piping.init_cond['T'].to(ht.ureg.K))
# ##    print (Test_piping.dP(m_dot))
# ##
# ##
# ##
# ##if __name__ == "__main__":
# ##        print (Ra().to_base_units())
# ##        print (gamma())
# ##        print (rp_init({'fluid':'helium', 'T':Q_(20,ht.ureg.degC), 'P':Q_(101325, ht.ureg.Pa)}))
# ##        print (rp_init({'fluid':'helium', 'T':Q_(4.2,ht.ureg.K), 'P':Q_(101325, ht.ureg.Pa)}))
# ##        print (satp(Q_(101325, ht.ureg.Pa), [1])['t'])
# ##        print ('Decorator test:', satp(Q_(101325, ht.ureg.Pa), [1]))
# ##        print(tc_304(150*ht.ureg.K))
# ##        Leak = tc_304(150*ht.ureg.K)*3.14159*0.125*ht.ureg.inch*0.035*ht.ureg.inch/(1*ht.ureg.ft)*300*ht.ureg.K
# ##        print(Leak)
# ##        print(Leak.to(ht.ureg.W))
# ##        print((Leak/(7*ht.ureg('kJ/kg'))).to(ht.ureg.g/ht.ureg.s))
# ##        print(therm_exp(ht.ureg('4.5 K'))*ht.ureg('20 ft').to(ht.ureg.inch))
