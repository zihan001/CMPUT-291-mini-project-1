-- some data to test on

insert into users values ('cmma', 'Connor', '123');
insert into users values ('kait', 'Kaitlyn', '456');

insert into songs values (50 , 'Unity', 165);
insert into songs values (51 , 'Xenogenesis', 177);
insert into songs values (52 , 'Jackpot', 123);
insert into songs values (53 , 'Spectre', 180);
insert into songs values (54 , 'Unity', 170);
insert into songs values (55 , 'Sing Me To Sleep', 150);
insert into songs values (56 , 'Levels', 160);
insert into songs values (57 , 'The Nights', 100);
insert into songs values (58 , 'Wake Me Up', 180);

insert into sessions values ('cmma', 1, '2022-09-20', '2022-09-22');
insert into sessions values ('cmma', 2, '2022-10-27', '2022-10-27');
insert into sessions values ('kait', 1, '2021-03-10', '2021-03-15');

insert into listen values ('cmma', 1, 50, 1);
insert into listen values ('cmma', 1, 57, 1);
insert into listen values ('cmma', 1, 58, 1);
insert into listen values ('cmma', 1, 54, 1);
insert into listen values ('cmma', 2, 55, 1);
insert into listen values ('kait', 1, 53, 1);
insert into listen values ('kait', 1, 50, 1);

insert into playlists values (70, 'EDM Tracks 1', 'cmma');
insert into playlists values (71, 'Now This is Music', 'kait');

insert into plinclude values (70, 57, 1);
insert into plinclude values (70, 58, 2);
insert into plinclude values (70, 54, 3);
insert into plinclude values (70, 50, 4);
insert into plinclude values (70, 55, 5);
insert into plinclude values (71, 54, 1);
insert into plinclude values (71, 57, 2);
insert into plinclude values (71, 50, 3);
insert into plinclude values (71, 52, 4);

insert into artists values ('ftrt', 'TheFatRat', 'German', '1234');
insert into artists values ('alwa', 'Alan Walker', 'Norwegian', '5678');
insert into artists values ('avic', 'Avicii', 'Swedish', '9012');

insert into perform values ('ftrt', 50);
insert into perform values ('ftrt', 51);
insert into perform values ('ftrt', 52);
insert into perform values ('alwa', 53);
insert into perform values ('alwa', 54);
insert into perform values ('alwa', 55);
insert into perform values ('avic', 56);
insert into perform values ('avic', 57);
insert into perform values ('avic', 58);
