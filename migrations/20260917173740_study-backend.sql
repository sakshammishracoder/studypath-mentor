-- Additive migration. No existing application data is removed.
CREATE TABLE public.study_state (
  user_id uuid PRIMARY KEY DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
  revision integer NOT NULL DEFAULT 1 CHECK (revision > 0),
  payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(payload) = 'object' AND octet_length(payload::text) <= 1048576),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.study_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_state FORCE ROW LEVEL SECURITY;
REVOKE ALL ON public.study_state FROM PUBLIC, anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.study_state TO authenticated;
CREATE POLICY study_state_owner ON public.study_state FOR ALL TO authenticated
  USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE TABLE public.study_documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
  object_key text NOT NULL UNIQUE,
  title text NOT NULL CHECK (length(title) BETWEEN 1 AND 160),
  byte_size integer NOT NULL CHECK (byte_size BETWEEN 1 AND 5242880),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (split_part(object_key, '/', 1) = user_id::text AND object_key !~ '\.\.' AND object_key LIKE '%.pdf')
);
CREATE INDEX study_documents_owner_date ON public.study_documents(user_id, created_at DESC);
ALTER TABLE public.study_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_documents FORCE ROW LEVEL SECURITY;
REVOKE ALL ON public.study_documents FROM PUBLIC, anon;
GRANT SELECT, INSERT, DELETE ON public.study_documents TO authenticated;
CREATE POLICY study_documents_owner ON public.study_documents FOR ALL TO authenticated
  USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- Storage bucket must first be created with:
-- npx @insforge/cli storage create-bucket study-pdfs --private
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
CREATE POLICY study_pdf_owner ON storage.objects FOR ALL TO authenticated
  USING (bucket = 'study-pdfs' AND split_part(key, '/', 1) = auth.uid()::text)
  WITH CHECK (bucket = 'study-pdfs' AND split_part(key, '/', 1) = auth.uid()::text
              AND key !~ '\.\.' AND key LIKE '%.pdf');
-- Restrictive guard protects this bucket even if another permissive policy is added.
CREATE POLICY study_pdf_guard ON storage.objects AS RESTRICTIVE FOR ALL TO public
  USING (bucket <> 'study-pdfs' OR split_part(key, '/', 1) = auth.uid()::text)
  WITH CHECK (bucket <> 'study-pdfs' OR (split_part(key, '/', 1) = auth.uid()::text
              AND key !~ '\.\.' AND key LIKE '%.pdf'));
