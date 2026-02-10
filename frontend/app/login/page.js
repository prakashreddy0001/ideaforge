import LoginContent from "./LoginContent";

export const metadata = {
  title: "Sign In",
  description: "Sign in to your IdeaForge account.",
  robots: {
    index: false,
    follow: true,
  },
};

export default function LoginPage() {
  return <LoginContent />;
}
