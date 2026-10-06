create table metropt (
	timestamp timestamp primary key,
	tp2 double precision NOT NULL,
	tp3 double precision NOT NULL,
	h1 double precision NOT NULL,
	dv_pressure double precision NOT NULL,
	reservoirs double precision NOT NULL,
	oil_temperature double precision NOT NULL,
	motor_current double precision NOT NULL,
	comp smallint not null,
	dv_electric smallint not null,
	towers smallint not null,
	mpg smallint not null,
	lps smallint not null,
	pressure_switch smallint not null,
	oil_level smallint not null,
	caudal_impulses smallint not null
	);

	ALTER TABLE metropt
    ADD CONSTRAINT metropt_comp_binary_check
        CHECK (comp IN (0, 1)),
    ADD CONSTRAINT metropt_dv_electric_binary_check
        CHECK (dv_electric IN (0, 1)),
    ADD CONSTRAINT metropt_towers_binary_check
        CHECK (towers IN (0, 1)),
    ADD CONSTRAINT metropt_mpg_binary_check
        CHECK (mpg IN (0, 1)),
    ADD CONSTRAINT metropt_lps_binary_check
        CHECK (lps IN (0, 1)),
    ADD CONSTRAINT metropt_pressure_switch_binary_check
        CHECK (pressure_switch IN (0, 1)),
    ADD CONSTRAINT metropt_oil_level_binary_check
        CHECK (oil_level IN (0, 1)),
    ADD CONSTRAINT metropt_caudal_impulses_binary_check
        CHECK (caudal_impulses IN (0, 1));