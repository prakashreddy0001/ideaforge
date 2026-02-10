import RegisterContent from "./RegisterContent";

export const metadata = {
  title: "Create Account",
  description: "Create your free IdeaForge account and start building.",
  robots: {
    index: false,
    follow: true,
  },
};

export default function RegisterPage() {
  return <RegisterContent />;
}
