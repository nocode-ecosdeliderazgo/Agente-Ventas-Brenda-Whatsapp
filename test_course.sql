-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.ai_course_session (
  id_session uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  session_index smallint,
  title character varying,
  objective character varying,
  duration_minutes bigint,
  scheduled_at timestamp without time zone,
  id_course_fk uuid,
  CONSTRAINT ai_course_session_pkey PRIMARY KEY (id_session),
  CONSTRAINT ai_course_session_id_course_fk_fkey FOREIGN KEY (id_course_fk) REFERENCES public.ai_courses(id_course)
);
CREATE TABLE public.ai_courses (
  id_course uuid NOT NULL DEFAULT gen_random_uuid(),
  Name character varying,
  Short_description character varying,
  Long_descrption character varying,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  session_count smallint,
  total_duration_min bigint,
  Price character varying,
  Currency character varying,
  course_url character varying,
  Purchase_url character varying,
  level character varying,
  language character varying,
  audience_category character varying,
  status character varying,
  start_date timestamp without time zone,
  end_date timestamp without time zone,
  roi character varying,
  modality character varying NOT NULL,
  CONSTRAINT ai_courses_pkey PRIMARY KEY (id_course)
);
CREATE TABLE public.ai_tema_activity (
  id_activity uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  id_course_fk uuid NOT NULL DEFAULT gen_random_uuid(),
  id_session_fk uuid NOT NULL DEFAULT gen_random_uuid(),
  item_session integer NOT NULL,
  item_type text NOT NULL,
  title_item character varying NOT NULL,
  CONSTRAINT ai_tema_activity_pkey PRIMARY KEY (id_activity),
  CONSTRAINT ai_tema_activity_id_session_fk_fkey FOREIGN KEY (id_session_fk) REFERENCES public.ai_course_session(id_session),
  CONSTRAINT ai_tema_activity_id_course_fk_fkey FOREIGN KEY (id_course_fk) REFERENCES public.ai_courses(id_course)
);
CREATE TABLE public.bond (
  id_bond bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  content text NOT NULL,
  type_bond character varying NOT NULL,
  id_courses_fk uuid,
  CONSTRAINT bond_pkey PRIMARY KEY (id_bond),
  CONSTRAINT Bond_id_courses_fk_fkey FOREIGN KEY (id_courses_fk) REFERENCES public.ai_courses(id_course)
);
CREATE TABLE public.elements_url (
  id_element uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  id_session_fk uuid NOT NULL DEFAULT gen_random_uuid(),
  id_activity_fk uuid DEFAULT gen_random_uuid(),
  item_type character varying NOT NULL,
  url_test character varying NOT NULL,
  description_url character varying NOT NULL,
  CONSTRAINT elements_url_pkey PRIMARY KEY (id_element),
  CONSTRAINT Elements_url_id_activity_fk_fkey FOREIGN KEY (id_activity_fk) REFERENCES public.ai_tema_activity(id_activity),
  CONSTRAINT Elements_url_id_session_fk_fkey FOREIGN KEY (id_session_fk) REFERENCES public.ai_course_session(id_session)
);