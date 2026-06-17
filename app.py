import streamlit as st
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session state initialisation ──────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Sidebar — owner + pet setup ───────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Owner Setup")
    owner_name = st.text_input("Your name", value="Jordan")
    if st.button("Set Owner", use_container_width=True):
        st.session_state.owner = Owner(owner_name)
        st.success(f"Owner set to {owner_name}")

    if st.session_state.owner:
        st.divider()
        st.header("🐾 Add a Pet")
        with st.form("add_pet_form"):
            pet_name = st.text_input("Pet name")
            pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
            if st.form_submit_button("Add Pet", use_container_width=True) and pet_name.strip():
                st.session_state.owner.add_pet(Pet(pet_name.strip(), pet_species))
                st.success(f"Added {pet_name}!")

# ── Guard: require owner ──────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — sort, filter, and manage daily tasks for all your pets.")

if st.session_state.owner is None:
    st.info("Enter your name in the sidebar and click **Set Owner** to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ── Main layout ───────────────────────────────────────────────────────────────
col_schedule, col_add = st.columns([3, 2])

# ── Left column: today's schedule ────────────────────────────────────────────
with col_schedule:
    st.header(f"Today's Schedule — {owner.name}")

    if not owner.pets:
        st.info("No pets yet. Add one in the sidebar.")
    else:
        schedule = scheduler.get_schedule()
        conflicts = scheduler.detect_conflicts(schedule)

        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

        if not schedule:
            st.info("No tasks scheduled for today. Add tasks on the right.")
        else:
            for pet, task in schedule:
                c1, c2, c3 = st.columns([1, 5, 1])
                with c1:
                    st.markdown(f"**{task.time}**")
                with c2:
                    icon = "✅" if task.completed else "⬜"
                    st.markdown(
                        f"{icon} **{task.description}** — *{pet.name}*  \n"
                        f"<small>{task.duration_minutes} min · {task.priority} priority · {task.frequency}</small>",
                        unsafe_allow_html=True,
                    )
                with c3:
                    btn_key = f"done_{pet.name}_{task.description}_{task.time}"
                    if not task.completed:
                        if st.button("Done ✓", key=btn_key):
                            next_t = scheduler.mark_task_complete(pet, task)
                            if next_t:
                                st.success(f"Rescheduled for {next_t.due_date}")
                            st.rerun()
                    else:
                        st.success("Done!")

# ── Right column: add task + filter ──────────────────────────────────────────
with col_add:
    st.header("Add a Task")

    if not owner.pets:
        st.info("Add a pet in the sidebar first.")
    else:
        pet_names = [p.name for p in owner.pets]
        with st.form("add_task_form"):
            selected_pet = st.selectbox("Pet", pet_names)
            task_desc = st.text_input("Description", value="Morning walk")
            task_time = st.text_input("Time (HH:MM)", value="08:00")
            task_dur = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            task_freq = st.selectbox("Frequency", ["once", "daily", "weekly"])
            task_pri = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            if st.form_submit_button("Add Task", use_container_width=True) and task_desc.strip():
                target = next(p for p in owner.pets if p.name == selected_pet)
                target.add_task(
                    Task(
                        description=task_desc.strip(),
                        time=task_time.strip(),
                        duration_minutes=int(task_dur),
                        frequency=task_freq,
                        priority=task_pri,
                        due_date=date.today(),
                    )
                )
                st.success(f"Task added for {selected_pet}!")
                st.rerun()

    st.divider()
    st.header("Filter Tasks")

    if owner.pets:
        filter_pet = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
        filter_status = st.selectbox("Status", ["All", "Pending", "Completed"])

        filtered = owner.get_all_tasks()
        if filter_pet != "All":
            filtered = scheduler.filter_by_pet(filter_pet, filtered)
        if filter_status == "Pending":
            filtered = scheduler.filter_by_status(False, filtered)
        elif filter_status == "Completed":
            filtered = scheduler.filter_by_status(True, filtered)

        filtered = scheduler.sort_by_time(filtered)

        if filtered:
            st.table(
                [
                    {
                        "Time": t.time,
                        "Pet": p.name,
                        "Task": t.description,
                        "Duration": f"{t.duration_minutes}m",
                        "Priority": t.priority,
                        "Status": "✅" if t.completed else "⬜",
                    }
                    for p, t in filtered
                ]
            )
        else:
            st.info("No tasks match the filter.")
