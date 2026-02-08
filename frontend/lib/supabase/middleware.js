import { createServerClient } from "@supabase/ssr";
import { NextResponse } from "next/server";

/**
 * Middleware that refreshes the Supabase auth session on every request
 * and controls route access based on the validated session.
 *
 * Uses createServerClient with getUser() to validate and refresh the
 * JWT on every request, ensuring the browser always receives fresh
 * session cookies after a page load or refresh.
 *
 * The setAll callback is implemented correctly to update both the
 * request cookies (for downstream Server Components) and the response
 * cookies (for the browser), which prevents the _removeSession()
 * cookie-wiping issue that occurs with incomplete implementations.
 */
export async function updateSession(request) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          // 1. Update request cookies so downstream Server Components
          //    can read the refreshed session.
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          // 2. Recreate the response with the updated request cookies.
          supabaseResponse = NextResponse.next({ request });
          // 3. Write cookies to the response so the browser receives
          //    the refreshed tokens.
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // Validate & refresh the session. getUser() sends the token to the
  // Supabase Auth server, which refreshes the access token if expired
  // and writes the new tokens via setAll. Do NOT replace with
  // getSession() — it only reads from storage without validation.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Protected routes — redirect to login if no valid session
  const protectedPaths = ["/dashboard", "/admin", "/generate", "/refine"];
  const isProtected = protectedPaths.some((p) =>
    request.nextUrl.pathname.startsWith(p)
  );

  if (isProtected && !user) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("redirect", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }

  // Redirect authenticated users away from auth pages
  const authPaths = ["/login", "/register"];
  if (authPaths.includes(request.nextUrl.pathname) && user) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return supabaseResponse;
}
