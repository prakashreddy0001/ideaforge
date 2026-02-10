import AdminLayoutContent from "./AdminLayoutContent";

export const metadata = {
  title: {
    default: "Admin",
    template: "%s | Admin | IdeaForge",
  },
  robots: {
    index: false,
    follow: false,
  },
};

export default function AdminLayout({ children }) {
  return <AdminLayoutContent>{children}</AdminLayoutContent>;
}
