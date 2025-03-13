import Navbar from "./Navbar";
import Home from "./Home";
import MyWallet from "./MyWallet";
import ViewExchangeHistory from "./ViewExchangeHistory";
import ViewOffers from "./ViewOffers";
import MakeOffer from "./MakeOffer";
import { useEffect, useState } from "react";

function Main({ isAuthenticated,setUserEmail }) {
    const [values, setValues] = useState([]);

    // Funkcja do obsługi dodawania wartości
    const [activeSection, setActiveSection] = useState('Home');
    const currencies = ['USD', 'EUR', 'PLN'];
    const renderSection = () => {
        switch (activeSection) {
            case 'Home':
                return <Home />;
            case 'MakeOffer':
                return <MakeOffer currencies={currencies} />;
            case 'ViewOffers':
                return <ViewOffers />;
            case 'ViewExchangeHistory':
                return <ViewExchangeHistory />;
            case 'MyWallet':
                return <MyWallet />;
            default:
                return <Home />;
        }
    };
    useEffect(() => {
        console.log(activeSection);
    }, [activeSection]);
    return (
        <div className="App">
            <Navbar setActiveSection={setActiveSection} isAuthenticated={isAuthenticated} setUserEmail = {setUserEmail}/>

            <div className={'content'}>
                {renderSection()}
            </div>
        </div>
    );
}

export default Main;
