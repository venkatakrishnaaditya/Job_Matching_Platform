import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";

import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import StudentDashboard from "./pages/StudentDashboard";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import UploadResume from "./pages/UploadResume";
import BrowseJobs from "./pages/BrowseJobs";
import MyApplications from "./pages/MyApplications";
import ViewApplicants from "./pages/ViewApplicants";
import PostJob from "./pages/PostJob";
import Profile from "./pages/Profile";
import EditProfile from "./pages/EditProfile";

/* Component to control Navbar visibility */
function Layout({ children }) {
  const location = useLocation();

  // Pages where Navbar should be hidden (only auth pages)
  const hideNavbarPaths = ["/login", "/register", "/forgot-password", "/reset-password"];

  const shouldHideNavbar = hideNavbarPaths.includes(location.pathname);

  return (
    <>
      {!shouldHideNavbar && <Navbar />}
      {children}
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {/* Public Pages */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* Student Pages */}
          <Route path="/student-dashboard" element={<StudentDashboard />} />
          <Route path="/upload-resume" element={<UploadResume />} />
          <Route path="/browse-jobs" element={<BrowseJobs />} />
          <Route path="/my-applications" element={<MyApplications />} />

          {/* Recruiter Pages */}
          <Route path="/recruiter-dashboard" element={<RecruiterDashboard />} />
          <Route path="/post-job" element={<PostJob />} />
          <Route path="/edit-job/:jobId" element={<PostJob />} />
          <Route path="/view-applicants/:jobId" element={<ViewApplicants />} />

          {/* Profile Pages (Common) */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/edit-profile" element={<EditProfile />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
