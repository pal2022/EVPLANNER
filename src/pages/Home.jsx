import Form from '../components/Form';
import styles from './Home.module.css';

export default function Home() {
  return (
    <div className={styles.pageContainer}>
      <h1 className={styles.heading}>EV Route Planner</h1>
      <Form />
    </div>
  );
}
