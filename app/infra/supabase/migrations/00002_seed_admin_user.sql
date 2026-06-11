-- Seed base platform admin (local dev only)
-- Login: admin@rpg.local / RpgAdmin!local
-- Idempotent: safe to re-run on db reset

DO $$
DECLARE
  v_admin_id uuid := 'a0000000-0000-4000-8000-000000000001';
  v_email text := 'admin@rpg.local';
  v_password text := 'RpgAdmin!local';
BEGIN
  IF NOT EXISTS (SELECT 1 FROM auth.users WHERE id = v_admin_id) THEN
  INSERT INTO auth.users (
    instance_id,
    id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    raw_app_meta_data,
    raw_user_meta_data,
    created_at,
    updated_at,
    confirmation_token,
    email_change,
    email_change_token_new,
    recovery_token
  )
  VALUES (
    '00000000-0000-0000-0000-000000000000',
    v_admin_id,
    'authenticated',
    'authenticated',
    v_email,
    crypt(v_password, gen_salt('bf')),
    now(),
    '{"provider":"email","providers":["email"]}',
    '{"full_name":"Admin"}',
    now(),
    now(),
    '',
    '',
    '',
    ''
  );
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM auth.identities
    WHERE user_id = v_admin_id AND provider = 'email'
  ) THEN
  INSERT INTO auth.identities (
    id,
    user_id,
    identity_data,
    provider,
    provider_id,
    last_sign_in_at,
    created_at,
    updated_at
  )
  VALUES (
    v_admin_id,
    v_admin_id,
    jsonb_build_object('sub', v_admin_id::text, 'email', v_email),
    'email',
    v_admin_id::text,
    now(),
    now(),
    now()
  );
  END IF;

  INSERT INTO public.users (
    id,
    email,
    display_name,
    status,
    is_admin
  )
  VALUES (
    v_admin_id,
    v_email,
    'Admin',
    'active',
    true
  )
  ON CONFLICT (id) DO UPDATE
    SET is_admin = EXCLUDED.is_admin,
        display_name = EXCLUDED.display_name,
        email = EXCLUDED.email,
        status = 'active',
        updated_at = now();

  RAISE NOTICE 'Seeded admin user: % (password in migration comment)', v_email;
END $$;
