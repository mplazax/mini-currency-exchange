import React, { useState } from 'react';
import {
    createBrowserRouter,
    RouterProvider
} from 'react-router-dom';
import Main from "./components/Main";
import Register from './components/Register';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ViewOffers from "./components/ViewOffers";
import MakeOffer from "./components/MakeOffer";
import MyWallet from "./components/MyWallet";

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userEmail, setUserEmail] = useState(null);
    const [myWallet, setMyWallet] = useState(null);

    const router = createBrowserRouter([
        {
            path: '/',
            element: <Main isAuthenticated={isAuthenticated} setUserEmail={setUserEmail} />
        },
        {
            path: '/register',
            element: <Register />
        },
        {
            path: '/login',
            element: <Login isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} setUserEmail={setUserEmail} />
        },
        {
            path: '/add_offer',  // Usunięto dodatkową spację na końcu
            element: <MakeOffer userEmail={userEmail} myWallet = {myWallet}/>
        },
        {
            path: '/get_offers',
            element: <ViewOffers userEmail = {userEmail} myWallet = {setMyWallet} setMyWallet = {setMyWallet}/>
        },
        {
            path: '/dashboard',
            element: <Dashboard />
        },
        {
            path: '/wallet',
            element: <MyWallet setMyWallet = {setMyWallet}/>
        }
    ]);

    return (
        <RouterProvider router={router}></RouterProvider>
    );
}

export default App;
