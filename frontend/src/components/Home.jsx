export default function Home(){
    return(
        <>
            <div className={'text'}>
            <h1>Sprawozdanie z analizy aplikacji minigiełdy walutowej</h1>
                <h2>Wprowadzenie</h2>
                <p>
                Przedstawiony projekt aplikacji minigiełdy walutowej wykorzystuje technologię Flask jako framework do budowy backendu oraz MongoDB jako bazę danych. Aplikacja umożliwia użytkownikom rejestrację, logowanie, dodawanie ofert wymiany walut, realizowanie transakcji oraz przeglądanie swoich transakcji i sald w portfelu.

                <h3>Zastosowane technologie</h3>
                <h5>Flask</h5>:
                <br/>
                Framework webowy oparty na Pythonie, używany do tworzenia serwera aplikacji.
                Flask-Login: rozszerzenie Flask do obsługi sesji użytkownika i zarządzania autoryzacją.
                Flask-CORS: pozwala na Cross-Origin Resource Sharing (CORS), co jest istotne dla integracji frontendu z backendem.<br/>
                <h5>MongoDB:</h5>

                Baza danych NoSQL, używana do przechowywania informacji o użytkownikach, ofertach wymiany walut, portfelach oraz transakcjach.
                <h5>PyMongo:</h5> oficjalny klient MongoDB dla Pythona, używany do komunikacji z bazą danych.

                <h2>Struktura bazy danych</h2>
                    <h5>Kolekcje:</h5>

                records: przechowuje informacje o użytkownikach (nazwa, email, hasło).<br/>
                offers: przechowuje oferty wymiany walut (użytkownik, waluty, wartości, data).<br/>
                wallets: przechowuje informacje o portfelach użytkowników (użytkownik, waluty i ich wartości).<br/>
                transactions: przechowuje zrealizowane transakcje (użytkownicy, waluty, wartości, data).<br/>
                <h5>Kluczowe funkcje aplikacji</h5>
                Rejestracja i logowanie użytkowników<br/>
                /register: Rejestracja nowych użytkowników, haszowanie hasła i tworzenie portfela z losowymi wartościami początkowymi dla różnych walut.<br/>
                /login: Logowanie użytkowników, weryfikacja hasła i inicjalizacja sesji.<br/>
                /logout: Wylogowanie użytkownika i usunięcie sesji.<br/>
                    <h5>Oferty wymiany walut</h5>
                /add_offer: Dodawanie nowych ofert wymiany walut. Sprawdzanie salda użytkownika, dopasowanie ofert i ewentualne realizowanie transakcji lub dodawanie nowej oferty.<br/>
                /get_offers: Pobieranie wszystkich dostępnych ofert wymiany.<br/>
                <h5>Transakcje</h5>
                /make_transaction/offer_id: Realizowanie transakcji na podstawie wybranej oferty, aktualizacja portfeli użytkowników i dodanie zapisu transakcji.<br/>
                    /all_transactions: Pobieranie wszystkich transakcji (wymaga zalogowania).<br/>
                    /my_transactions: Pobieranie transakcji zalogowanego użytkownika.<br/>
                    <h5>Portfele użytkowników</h5>
                    /wallet: Pobieranie salda portfela i historii transakcji zalogowanego użytkownika.<br/>
                    <h5>Anulowanie ofert</h5>
                    /cancel_offer/offer_id: Anulowanie wybranej oferty i zwrot wartości waluty do portfela użytkownika.<br/>
                        <h3>Wnioski</h3>
                        <h5>Skalowalność:</h5>

                        Wykorzystanie MongoDB jako bazy danych pozwala na łatwe skalowanie aplikacji w przypadku wzrostu liczby użytkowników i transakcji.
                        Architektura oparta na Flask umożliwia łatwą integrację z frontendem i dalszy rozwój aplikacji.
                    <h5>Funkcjonalność:</h5>

                        Aplikacja oferuje podstawowe funkcje niezbędne do obsługi wymiany walut: rejestracja, logowanie, dodawanie ofert, realizowanie transakcji oraz przeglądanie sald i historii transakcji.
                        Implementacja logiki biznesowej, takiej jak sprawdzanie salda przed dodaniem oferty czy realizowanie transakcji na podstawie najlepszych dostępnych ofert, jest przemyślana i dobrze zrealizowana.
                </p>
            </div>
            </>
    );
}