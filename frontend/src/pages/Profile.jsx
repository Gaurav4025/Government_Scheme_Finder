import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import axios from "../lib/axios";
import toast from "react-hot-toast";

export default function Profile() {
  const [form, setForm] = useState({
    name: "",
    dob: "",
    state: "",
    income: "",
    category: ""
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.name || !form.dob || !form.state || !form.income || !form.category) {
      toast.error("Please fill all fields");
      return;
    }

    try {
      setLoading(true);

      // 1️⃣ Save profile to backend
      await axios.post("/api/profile/basic", {
        name: form.name,
        dob: form.dob,
        state: form.state,
        income: Number(form.income),
        category: form.category
      });

      // 2️⃣ Update local auth state
      const authUser = JSON.parse(localStorage.getItem("authUser"));

      const updatedUser = {
        ...authUser,
        profileCompleted: true
      };

      localStorage.setItem("authUser", JSON.stringify(updatedUser));

      toast.success("Profile saved successfully");

      // 3️⃣ Reload → Index.jsx will route correctly
      window.location.href = "/";

    } catch (err) {
      console.error(err);
      toast.error("Failed to save profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Complete Your Profile</CardTitle>
        </CardHeader>

        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <Input name="name" placeholder="Full Name" onChange={handleChange} />
            <Input name="dob" type="date" onChange={handleChange} />
            <Input name="state" placeholder="State" onChange={handleChange} />
            <Input name="income" type="number" placeholder="Annual Income" onChange={handleChange} />

            <select
              name="category"
              onChange={handleChange}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Select Category</option>
              <option value="GEN">General</option>
              <option value="OBC">OBC</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
            </select>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Saving..." : "Save Profile"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
