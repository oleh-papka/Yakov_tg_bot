--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: city; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.city (
    id integer NOT NULL,
    owm_id integer NOT NULL,
    name character varying(50) NOT NULL,
    local_name character varying(50),
    lat real,
    lon real,
    sinoptik_url text,
    timezone_offset integer
);


--
-- Name: city_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.city_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.city_id_seq OWNED BY public.city.id;


--
-- Name: crypto_currency; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crypto_currency (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    abbr character varying(10) NOT NULL
);


--
-- Name: crypto_currency_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.crypto_currency_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: crypto_currency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.crypto_currency_id_seq OWNED BY public.crypto_currency.id;


--
-- Name: crypto_currency_watchlist; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crypto_currency_watchlist (
    user_id integer NOT NULL,
    crypto_currency_id integer NOT NULL
);


--
-- Name: currency; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.currency (
    id integer NOT NULL,
    name character varying(5) NOT NULL,
    symbol character varying(5) NOT NULL
);


--
-- Name: currency_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.currency_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: currency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.currency_id_seq OWNED BY public.currency.id;


--
-- Name: currency_watchlist; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.currency_watchlist (
    user_id integer NOT NULL,
    currency_id integer NOT NULL
);


--
-- Name: feedback; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feedback (
    id integer NOT NULL,
    user_id integer NOT NULL,
    msg_id integer NOT NULL,
    msg_text text NOT NULL,
    read_flag boolean NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


--
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feedback_id_seq OWNED BY public.feedback.id;


--
-- Name: feedback_reply; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feedback_reply (
    id integer NOT NULL,
    feedback_id integer NOT NULL,
    msg_id integer NOT NULL,
    msg_text text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


--
-- Name: feedback_reply_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feedback_reply_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feedback_reply_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feedback_reply_id_seq OWNED BY public.feedback_reply.id;


--
-- Name: repeated_action; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.repeated_action (
    id integer NOT NULL,
    user_id integer NOT NULL,
    action character varying(30) NOT NULL,
    execution_time time without time zone NOT NULL
);


--
-- Name: repeated_action_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.repeated_action_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: repeated_action_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.repeated_action_id_seq OWNED BY public.repeated_action.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(64),
    first_name character varying(64) NOT NULL,
    last_name character varying(64),
    joined timestamp without time zone NOT NULL,
    language_code character varying(2) NOT NULL,
    timezone_offset integer,
    active boolean NOT NULL,
    city_id integer
);


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: city id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.city ALTER COLUMN id SET DEFAULT nextval('public.city_id_seq'::regclass);


--
-- Name: crypto_currency id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_currency ALTER COLUMN id SET DEFAULT nextval('public.crypto_currency_id_seq'::regclass);


--
-- Name: currency id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currency ALTER COLUMN id SET DEFAULT nextval('public.currency_id_seq'::regclass);


--
-- Name: feedback id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback ALTER COLUMN id SET DEFAULT nextval('public.feedback_id_seq'::regclass);


--
-- Name: feedback_reply id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback_reply ALTER COLUMN id SET DEFAULT nextval('public.feedback_reply_id_seq'::regclass);


--
-- Name: repeated_action id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.repeated_action ALTER COLUMN id SET DEFAULT nextval('public.repeated_action_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
0006
\.


--
-- Data for Name: city; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.city (id, owm_id, name, local_name, lat, lon, sinoptik_url, timezone_offset) FROM stdin;
\.


--
-- Data for Name: crypto_currency; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.crypto_currency (id, name, abbr) FROM stdin;
1	Bitcoin	BTC
1027	Ethereum	ETH
1839	BNB	BNB
5426	Solana	SOL
52	XRP	XRP
74	Dogecoin	DOGE
\.


--
-- Data for Name: crypto_currency_watchlist; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.crypto_currency_watchlist (user_id, crypto_currency_id) FROM stdin;
\.


--
-- Data for Name: currency; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.currency (id, name, symbol) FROM stdin;
1	usd	🇺🇸
2	eur	🇪🇺
3	pln	🇵🇱
4	gbp	🇬🇧
\.


--
-- Data for Name: currency_watchlist; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.currency_watchlist (user_id, currency_id) FROM stdin;
\.


--
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feedback (id, user_id, msg_id, msg_text, read_flag, "timestamp") FROM stdin;
\.


--
-- Data for Name: feedback_reply; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feedback_reply (id, feedback_id, msg_id, msg_text, "timestamp") FROM stdin;
\.


--
-- Data for Name: repeated_action; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.repeated_action (id, user_id, action, execution_time) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, username, first_name, last_name, joined, language_code, timezone_offset, active, city_id) FROM stdin;
\.


--
-- Name: city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.city_id_seq', 1, false);


--
-- Name: crypto_currency_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.crypto_currency_id_seq', 1, false);


--
-- Name: currency_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.currency_id_seq', 4, true);


--
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.feedback_id_seq', 1, false);


--
-- Name: feedback_reply_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.feedback_reply_id_seq', 1, false);


--
-- Name: repeated_action_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.repeated_action_id_seq', 1, false);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: city city_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.city
    ADD CONSTRAINT city_pkey PRIMARY KEY (id);


--
-- Name: crypto_currency crypto_currency_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_currency
    ADD CONSTRAINT crypto_currency_pkey PRIMARY KEY (id);


--
-- Name: crypto_currency_watchlist crypto_currency_watchlist_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_currency_watchlist
    ADD CONSTRAINT crypto_currency_watchlist_pkey PRIMARY KEY (user_id, crypto_currency_id);


--
-- Name: currency currency_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currency
    ADD CONSTRAINT currency_pkey PRIMARY KEY (id);


--
-- Name: currency_watchlist currency_watchlist_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currency_watchlist
    ADD CONSTRAINT currency_watchlist_pkey PRIMARY KEY (user_id, currency_id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: feedback_reply feedback_reply_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback_reply
    ADD CONSTRAINT feedback_reply_pkey PRIMARY KEY (id);


--
-- Name: repeated_action repeated_action_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.repeated_action
    ADD CONSTRAINT repeated_action_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: crypto_currency_watchlist crypto_currency_watchlist_crypto_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_currency_watchlist
    ADD CONSTRAINT crypto_currency_watchlist_crypto_currency_id_fkey FOREIGN KEY (crypto_currency_id) REFERENCES public.crypto_currency(id);


--
-- Name: crypto_currency_watchlist crypto_currency_watchlist_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_currency_watchlist
    ADD CONSTRAINT crypto_currency_watchlist_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: currency_watchlist currency_watchlist_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currency_watchlist
    ADD CONSTRAINT currency_watchlist_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currency(id);


--
-- Name: currency_watchlist currency_watchlist_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.currency_watchlist
    ADD CONSTRAINT currency_watchlist_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: feedback_reply feedback_reply_feedback_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback_reply
    ADD CONSTRAINT feedback_reply_feedback_id_fkey FOREIGN KEY (feedback_id) REFERENCES public.feedback(id);


--
-- Name: feedback feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: repeated_action repeated_action_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.repeated_action
    ADD CONSTRAINT repeated_action_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: user user_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.city(id);


--
-- PostgreSQL database dump complete
--

